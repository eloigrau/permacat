from django import forms
from .models import Article, Commentaire, Evenement, Participation
from django.utils.text import slugify
import itertools
#from django.utils.formats import localize
#from tinymce.widgets import TinyMCE
from django_summernote.widgets import SummernoteWidget, SummernoteWidgetBase, SummernoteInplaceWidget
from django.urls import reverse
from bourseLibre.settings import SUMMERNOTE_CONFIG as summernote_config
from django.contrib.staticfiles.templatetags.staticfiles import static



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

    class Meta:
        model = Article
        fields = ['jardin', 'categorie', 'titre', 'contenu', 'start_time', 'end_time', 'estModifiable']
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

    def save(self, userProfile, sendMail=True):
        instance = super(ArticleForm, self).save(commit=False)

        max_length = Article._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Article.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        instance.save(sendMail)

        return instance


class ArticleChangeForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['jardin', 'categorie', 'titre', 'contenu', 'start_time', 'end_time', 'estModifiable', 'estArchive']
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

class CommentaireArticleForm(forms.ModelForm):

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


class EvenementForm(forms.ModelForm):
    article = forms.ModelChoiceField(queryset=Article.objects.all().order_by('titre') ) #forms.ChoiceField(choices=Article.objects.all())

    class Meta:
        model = Evenement
        fields = ['start_time', 'titre_even', 'article', 'end_time', ]
        widgets = {
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


class EvenementArticleForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['start_time', 'titre_even', 'end_time', ]
        widgets = {
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

    def save(self, id_article):
        instance = super(EvenementArticleForm, self).save(commit=False)
        article = Article.objects.get(id=id_article)
        instance.article = article
        if not Evenement.objects.filter(start_time=instance.start_time, article=article):
            instance.save()
        return instance



class accepterParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['participe']
