from django import forms
from .models import Atelier, CommentaireAtelier, Atelier
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget

class AtelierForm(forms.ModelForm):
    objectif = forms.CharField(label="Objectif de l'atelier", strip=False)

    class Meta:
        model = Atelier
        fields = ['statut', 'categorie', 'titre', 'référent', 'objectif', 'description', 'matériel', 'date_atelier', 'tags']
        widgets = {
            'description': SummernoteWidget(),
            'matériel': SummernoteWidget(),
            'date_atelier': forms.DateInput(attrs={'type':"date"}),
        }

    def save(self, userProfile):
        instance = super(AtelierForm, self).save(commit=False)

        max_length = Atelier._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Atelier.objects.filter(slug=instance.slug).exists():
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
        super(AtelierForm, self).__init__(request, *args, **kwargs)
        self.fields['description'].strip = False

class AtelierChangeForm(forms.ModelForm):


    class Meta:
        model = Atelier
        fields = ['statut', 'categorie', 'titre', 'référent', 'objectif', 'description', 'matériel', 'date_atelier', 'tags']
        widgets = {
            'description': SummernoteWidget(),
            'matériel': SummernoteWidget(),
            'date_atelier': forms.DateInput(attrs={'type':"date"}),
        }


    def __init__(self, *args, **kwargs):
        super(AtelierChangeForm, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False

class CommentaireAtelierForm(forms.ModelForm):
    commentaire = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}), label='Laisser un commentaire...')

    class Meta:
        model = CommentaireAtelier
        exclude = ['atelier','auteur_comm']
        #
        #widgets = {
         #  'commentaire': SummernoteWidget(),
        #        'commentaire': forms.Textarea(attrs={'rows': 1}),
         #   }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireAtelierForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False
