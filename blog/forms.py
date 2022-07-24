from django import forms

from django.http import HttpResponseRedirect
from formtools.preview import FormPreview
from .models import Article, Commentaire, Projet, CommentaireProjet, Evenement, AdresseArticle, Discussion
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from django.urls import reverse
from bourseLibre.settings import SUMMERNOTE_CONFIG as summernote_config
from bourseLibre.models import Asso
from django.contrib.staticfiles.templatetags.staticfiles import static
from photologue.models import Album
from .models import Choix
from django.core.exceptions import ValidationError
import re

class DateInput(forms.DateInput):
    input_type = 'date'

class SummernoteWidgetWithCustomToolbar(SummernoteWidget):
    def summernote_settings(self):
        summernote_settings = summernote_config.get('summernote', {}).copy()

        lang = summernote_config['summernote'].get('lang')
        if not lang:
            lang = 'fr-FR'
        summernote_settings.update({
            'lang': lang,
            'url': {
                'language': static('summernote/lang/summernote-' + lang + '.min.js'),
                'upload_attachment': reverse('django_summernote-upload_attachment'),
            },
                # As an example, using Summernote Air-mode
                'airMode': False,
                'iFrame': False,

                # Change editor size
                'width': '100%',
                'height': '250',

                # Use proper language setting automatically (default)

            "toolbar": [
                ['style', ['bold', 'italic', 'underline', 'clear', 'style', ]],
                ['fontsize', ['fontsize']],
                ['fontSizes', ['8', '9', '10', '11', '12', '14', '18', '22', '24', '36']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['link', ['link', 'picture', 'video', 'table', 'hr', ]],
                ['misc', ['undo', 'redo', 'help', 'fullscreen', 'codeview', 'readmore']],

            ],
            "popover": {
                "image": [
                    ['imagesize', ['imageSize100', 'imageSize50', 'imageSize25']],
                    ['float', ['floatLeft', 'floatRight', 'floatNone']],
                    ['remove', ['removeMedia']]
                ],
                "link": [
                    ['link', ['linkDialogShow', 'unlink']]
                ],
                "air": [
                ['style', ['bold', 'italic', 'underline', 'clear', 'style', ]],
                ['fontsize', ['fontsize']],
                ['fontSizes', ['8', '9', '10', '11', '12', '14', '18', '22', '24', '36']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['link', ['link', 'picture', 'video', 'table', 'hr', ]],
                ['misc', ['undo', 'redo', 'help', 'fullscreen']],
                ]
            },
        })
        return summernote_settings

class ArticleForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().order_by("id"), required=True,
                              label="Article public ou réservé aux membres du groupe :", )

    class Meta:
        model = Article
        fields = ['asso', 'categorie', 'titre', 'contenu', 'start_time', 'estModifiable', 'estEpingle','tags']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time':  forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),

           # 'bar': SummernoteInplaceWidget(),
        }

    def save(self, userProfile, sendMail=True):
        instance = super(ArticleForm, self).save(commit=False)

        max_length = Article._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Article.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        if len(re.findall(r"[A-Z]", instance.titre)) > 7:
            instance.titre = instance.titre.title()
        instance.auteur = userProfile

        instance.save()

        return instance

    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [('', '(Choisir un groupe)'), ] + [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]
        self.fields["categorie"].choices = [('', '(Choisir un groupe)'), ] #+ list(Choix.get_type_annonce_asso(""))

        if 'asso' in self.data:
            try:
                asso_id = int(self.data.get('asso'))
                nomAsso = Asso.objects.get(id=asso_id).abreviation
                self.fields["categorie"].choices = Choix.get_type_annonce_asso(nomAsso)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields["categorie"].choices = Choix.get_type_annonce_asso("")

class ArticleChangeForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['asso', 'categorie', 'titre', 'contenu', 'album', 'start_time', 'tags', 'estModifiable', 'estArchive', 'estEpingle',]
        widgets = {
            'contenu': SummernoteWidget(),
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, sendMail=True, commit=True):
        return super(ArticleChangeForm, self).save(commit=commit)

class ArticleAddAlbum(forms.ModelForm):
    album = forms.ModelChoiceField(queryset=Album.objects.all(), required=True,
                              label="Si l'album existe déjà sur le site, choisissez l'album photo à associer ci-dessous", )

    class Meta:
        model = Article
        fields = ['album',]


class DiscussionForm(forms.ModelForm):

    class Meta:
        model = Discussion
        exclude = ['article', 'slug']

    def valider_unique(self, article):
        cleaned_data = self.cleaned_data

        try:
            Discussion.objects.get(slug=slugify(cleaned_data['titre']), article=article)
        except Discussion.DoesNotExist:
            pass
        else:
            raise ValidationError('Il existe déjà une discussion avec ce titre pour cet article')

        # Always return cleaned_data
        return cleaned_data

class CommentaireArticleForm(forms.ModelForm):

    class Meta:
        model = Commentaire
        exclude = ['article', 'auteur_comm', 'discussion']
        #
        widgets = {
         'commentaire': SummernoteWidgetWithCustomToolbar(),
        }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireArticleForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False

class CommentaireArticleChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = Commentaire
        exclude = ['article', 'auteur_comm', 'discussion']

    #def __init__(self, request, article=None, *args, **kwargs):
    #    super(CommentaireArticleChangeForm, self).__init__(request, *args, **kwargs)
     #   self.fields['commentaire'].strip = False
        #if article:
        #    self.fields['discussion'] = forms.ModelChoiceField(queryset=Discussion.objects.filter(article=article), required=True,)


class ProjetForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                              label="Projet public ou réservé aux adhérents de l'asso :", )
    class Meta:
        model = Projet
        fields = ['asso', 'categorie', 'coresponsable', 'titre', 'contenu', 'statut', 'tags',  'start_time']
        widgets = {
        'contenu': SummernoteWidget(),
              'start_time':forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def __init__(self, request, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]

    def save(self, userProfile, sendMail=True):
        instance = super(ProjetForm, self).save(commit=False)

        max_length = Projet._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Projet.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        instance.save(sendMail)

        return instance


class ProjetChangeForm(forms.ModelForm):

    class Meta:
        model = Projet
        fields = ['asso', 'categorie', 'coresponsable', 'titre', 'contenu', 'tags', 'lien_document', 'start_time', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

class CommentProjetForm(forms.ModelForm):

    class Meta:
        model = CommentaireProjet
        exclude = ['projet','auteur_comm']

        widgets = {
                'commentaire': SummernoteWidgetWithCustomToolbar(),
            }

    def __init__(self, request, *args, **kwargs):
         super(CommentProjetForm, self).__init__(request, *args, **kwargs)
         self.fields['commentaire'].strip = False


class CommentaireProjetChangeForm(forms.ModelForm):
     commentaire = forms.CharField(required=False, widget=SummernoteWidget())

     class Meta:
         model = CommentaireProjet
         exclude = ['projet', 'auteur_comm']
         widgets = {
             'commentaire': SummernoteWidget(),
         }


class EvenementForm(forms.ModelForm):
    qs = Article.objects.filter(estArchive=False)
    article = forms.ModelChoiceField(queryset=qs.order_by('titre')) #forms.ChoiceField(choices=Article.objects.all())

    class Meta:
        model = Evenement
        fields = ['start_time', 'titre_even', 'article', ]
        widgets = {
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, request):
        instance = super(EvenementForm, self).save(commit=False)
        instance.auteur = request.user
        instance.save()
        return instance

class EvenementArticleForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['start_time', 'titre_even', ]
        widgets = {
            'start_time':forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def save(self, request, id_article):
        instance = super(EvenementArticleForm, self).save(commit=False)
        article = Article.objects.get(id=id_article)
        instance.article = article
        instance.auteur = request.user
        instance.save()
        return instance

class AdresseArticleForm(forms.ModelForm):
    class Meta:
        model = AdresseArticle
        fields = ['titre',]

    def save(self, article, adresse):
        instance = super(AdresseArticleForm, self).save(commit=False)
        instance.article = article
        instance.adresse = adresse
        instance.save()
        return instance
