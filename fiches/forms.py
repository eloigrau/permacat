from django import forms
from .models import Fiche, CommentaireFiche, Atelier
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget

class FicheForm(forms.ModelForm):
    objectif = forms.CharField(label="Objectif de la fiche", strip=False)

    class Meta:
        model = Fiche
        fields = ['categorie', 'numero', 'titre', 'objectif', 'contenu', 'en_savoir_plus', 'tags']
        widgets = {
            'contenu': SummernoteWidget(),
            'en_savoir_plus': SummernoteWidget(),
        }

    def save(self, userProfile):
        instance = super(FicheForm, self).save(commit=False)

        max_length = Fiche._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Fiche.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.save()
        try:
            instance.save_m2m()
        except:
            pass

        return instance


    def __init__(self, request, *args, **kwargs):
        super(FicheForm, self).__init__(request, *args, **kwargs)
        self.fields['contenu'].strip = False

class FicheChangeForm(forms.ModelForm):
    objectif = forms.CharField(label="Objectif de la fiche", strip=False)


    class Meta:
        model = Fiche
        fields = ['categorie', 'numero', 'titre', 'objectif', 'contenu', 'en_savoir_plus', 'tags']
        widgets = {
            'contenu': SummernoteWidget(),
            'en_savoir_plus': SummernoteWidget(),
        }


    def __init__(self, *args, **kwargs):
        super(FicheChangeForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False

class AtelierForm(forms.ModelForm):
    class Meta:
        model = Atelier
        fields = ['categorie', 'titre', 'contenu' ,'age' ,'difficulte' ,'budget' ,'temps']
        widgets = {
            'contenu': SummernoteWidget(),
           # 'bar': SummernoteInplaceWidget(),
        }

    def save(self, fiche):
        instance = super(AtelierForm, self).save(commit=False)

        instance.fiche = fiche
        max_length = Atelier._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Atelier.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.save()

        return instance


    def __init__(self, request, *args, **kwargs):
        super(AtelierForm, self).__init__(request, *args, **kwargs)
        self.fields['contenu'].strip = False

class AtelierChangeForm(forms.ModelForm):

    class Meta:
        model = Atelier
        fields = ['categorie', 'titre', 'contenu', 'age' ,'difficulte' ,'budget' ,'temps']
        widgets = {
            'contenu': SummernoteWidget(),
        }


    def __init__(self, *args, **kwargs):
        super(AtelierChangeForm, self).__init__(*args, **kwargs)
        self.fields['contenu'].strip = False


class CommentaireFicheForm(forms.ModelForm):
    commentaire = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}), label='Laisser un commentaire...')

    class Meta:
        model = CommentaireFiche
        exclude = ['fiche','auteur_comm']
        #
        #widgets = {
         #  'commentaire': SummernoteWidget(),
        #        'commentaire': forms.Textarea(attrs={'rows': 1}),
         #   }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireFicheForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False
