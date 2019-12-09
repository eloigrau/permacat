from django import forms
from .models import Atelier, CommentaireAtelier, Atelier, InscriptionAtelier
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from bourseLibre.models import Profil

class AtelierForm(forms.ModelForm):
    referent = forms.ChoiceField(label='Référent atelier')

    class Meta:
        model = Atelier
        fields = ['statut', 'categorie', 'titre', 'referent', 'description', 'materiel', 'date_atelier','heure_atelier']
        widgets = {
            'description': SummernoteWidget(),
            'materiel': SummernoteWidget(),
            'date_atelier': forms.DateInput(attrs={'type':"date"}),
            'heure_atelier': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
        }

    def save(self):
        instance = super(AtelierForm, self).save(commit=False)
        referent = self.cleaned_data['referent']
        instance.referent = dict(self.fields['referent'].choices)[referent]


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
        self.fields['referent'].choices = [(i,u) for i, u in enumerate(Profil.objects.all().order_by('username'))]

class AtelierChangeForm(forms.ModelForm):
    referent = forms.ChoiceField(label='Référent atelier')

    class Meta:
        model = Atelier
        fields = ['statut', 'categorie', 'titre', 'referent', 'description', 'materiel', 'date_atelier',  'heure_atelier']
        widgets = {
            'description': SummernoteWidget(),
            'materiel': SummernoteWidget(),
            'date_atelier': forms.DateInput(attrs={'type':"date"}),
            'heure_atelier': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
        }


    def __init__(self, *args, **kwargs):
        super(AtelierChangeForm, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        self.fields['referent'].choices = [(i,u) for i, u in enumerate(Profil.objects.all().order_by('username'))]


    def save(self):
        instance = super(AtelierChangeForm, self).save(commit=False)
        referent = int(self.cleaned_data['referent'])
        instance.referent = dict(self.fields['referent'].choices)[referent].username
        instance.save()
        return instance

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

class CommentaireAtelierChangeForm(forms.ModelForm):

    class Meta:
        model = CommentaireAtelier
        exclude = ['atelier','auteur_comm']
        widgets = {
            'commentaire': SummernoteWidget(),
        }

class ContactParticipantsForm(forms.Form):

    msg = forms.CharField(label="Message", widget=SummernoteWidget)
    renvoi = forms.BooleanField(label="recevoir une copie",
                                     help_text="Cochez si vous souhaitez obtenir une copie du mail envoyé.", required=False
                                 )
