from django import forms
from .models import Article, Commentaire, Projet, CommentaireProjet, Evenement
from django.utils.text import slugify
import itertools
#from django.utils.formats import localize
#from tinymce.widgets import TinyMCE
from django_summernote.widgets import SummernoteWidget, SummernoteWidgetBase, SummernoteInplaceWidget
from django.urls import reverse
from bourseLibre.settings import SUMMERNOTE_CONFIG as summernote_config
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.timezone import now


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
   # contenu = TinyMCE(attrs={'cols': 80, 'rows': 20})
    estPublic = forms.ChoiceField(choices=((1, "Article public"), (0, "Article Permacat")), label='', required=True, )

    class Meta:
        model = Article
        fields = ['categorie', 'titre', 'contenu', 'start_time', 'end_time', 'estPublic', 'estModifiable']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'type': 'date'}),
              'end_time': forms.DateInput(attrs={'type': 'date'}),

           # 'bar': SummernoteInplaceWidget(),
        }

    def save(self, userProfile):
        instance = super(ArticleForm, self).save(commit=False)

        max_length = Article._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Article.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile
        if not userProfile.is_permacat:
            instance.estPublic = True

        instance.save()

        return instance


    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(request, *args, **kwargs)
        self.fields['contenu'].strip = False


class ArticleChangeForm(forms.ModelForm):
    estPublic = forms.ChoiceField(choices=((1, "Article public"), (0, "Article réservé aux adhérents")), label='', required=True)

    class Meta:
        model = Article
        fields = ['categorie', 'titre', 'contenu', 'start_time', 'end_time', 'estPublic', 'estModifiable', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'class':"date", }),
              'end_time': forms.DateInput(attrs={'class':'date', }),
        }


    def __init__(self, *args, **kwargs):
        super(ArticleChangeForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False
        self.fields["estPublic"].choices=((1, "Article public"), (0, "Article réservé aux adhérents")) if kwargs['instance'].estPublic else ((0, "Article réserve aux adhérents"),(1, "Article public"), )


#     def save(self,):
#         instance = super(ArticleChangeForm, self).save(commit=False)
#         instance.date_modification = now
# #        instance.save()
#         return instance

class CommentaireArticleForm(forms.ModelForm):
    #commentaire = TinyMCE(attrs={'cols': 1, 'rows': 1, 'height':10 })

    class Meta:
        model = Commentaire
        exclude = ['article','auteur_comm']
        #
        widgets = {
         'commentaire': SummernoteWidgetWithCustomToolbar(),
               # 'commentaire': forms.Textarea(attrs={'rows': 1}),
            }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireArticleForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False



class CommentaireArticleChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
     model = Commentaire
     exclude = ['article', 'auteur_comm']

class ProjetForm(forms.ModelForm):
    #contenu = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}))
    #contenu = TinyMCE(attrs={'cols': 80, 'rows': 20})
    estPublic = forms.ChoiceField(choices=((1, "Projet public"), (0, "Projet Permacat")), label='', required=True)

    class Meta:
        model = Projet
        fields = ['categorie', 'coresponsable', 'titre', 'contenu', 'statut', 'estPublic', 'lien_document', 'fichier_projet', 'start_time', 'end_time',]
        widgets = {
        'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'type':'date'}),
              'end_time': forms.DateInput(attrs={'type':'date'}),
        }

    def __init__(self, request, *args, **kwargs):
        super(ProjetForm, self).__init__(request, *args, **kwargs)
        self.fields['contenu'].strip = False

    def save(self, userProfile):
        instance = super(ProjetForm, self).save(commit=False)

        max_length = Projet._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Projet.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        if not userProfile.is_permacat:
            instance.estPublic = True

        instance.save()

        return instance


class ProjetChangeForm(forms.ModelForm):
    estPublic = forms.ChoiceField(choices=((1, "Projet public"), (0, "Projet réservé aux adhérents")), label='', required=True)

    class Meta:
        model = Projet
        fields = ['categorie', 'coresponsable', 'titre', 'contenu', 'estPublic', 'lien_document','fichier_projet', 'start_time', 'end_time', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'class':'date', }),
              'end_time': forms.DateInput(attrs={'class':'date', }),
        }

    def __init__(self, *args, **kwargs):
        super(ProjetChangeForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False
        self.fields["estPublic"].choices = ((1, "Article public"), (0, "Article réservé aux adhérents")) if kwargs[
            'instance'].estPublic else ((0, "Projet réservé aux adhérents"), (1, "Projet public"),)


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
    article = forms.ModelChoiceField(queryset=Article.objects.all() ) #forms.ChoiceField(choices=Article.objects.all())

    class Meta:
        model = Evenement
        fields = ['start_time', 'titre', 'article', 'end_time', ]
        widgets = {
            'start_time': forms.DateInput(attrs={'type': 'date'}),
            'end_time': forms.DateInput(attrs={'type': 'date'}),
        }


class EvenementArticleForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['start_time', 'titre', 'end_time', ]
        widgets = {
            'start_time': forms.DateInput(attrs={'type': 'date'}),
            'end_time': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, id_article):
        instance = super(EvenementArticleForm, self).save(commit=False)
        article = Article.objects.get(id=id_article)
        instance.article = article
        if not Evenement.objects.filter(start_time=instance.start_time, article=article):
            instance.save()
        return instance