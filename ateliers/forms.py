from django import forms
from .models import Atelier, CommentaireAtelier, Atelier, InscriptionAtelier
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from bourseLibre.models import Profil
from blog.forms import SummernoteWidgetWithCustomToolbar
from bourseLibre.models import Asso
from django.utils.timezone import now
from django.shortcuts import redirect
import re

class AtelierForm(forms.ModelForm):
    referent = forms.ChoiceField(label='Référent atelier')
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                                  label="Atelier public ou réservé aux adhérents de l'asso :", )

    class Meta:
        model = Atelier
        fields = ['titre', 'asso', 'statut', 'categorie', 'referent', 'description', 'materiel', 'start_time','heure_atelier','heure_atelier_fin', 'tarif_par_personne']
        widgets = {
            'description': SummernoteWidget(),
            'materiel': SummernoteWidget(),
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'heure_atelier': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
            'duree_prevue': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
        }

    def save(self, request, article):
        instance = super(AtelierForm, self).save(commit=False)
        try:
            referent = int(self.cleaned_data['referent'])
            instance.referent = dict(self.fields['referent'].choices)[referent].username
        except:
            instance.referent = dict(self.fields['referent'].choices)[referent]
            pass


        if len(re.findall(r"[A-Z]", instance.titre)) > 7:
            instance.titre = instance.titre.title()

        if article:
            instance.article = article

        max_length = Atelier._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]
        for x in itertools.count(1):
            if not Atelier.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = request.user
        instance.save()
        try:
            instance.save()
        except:
            pass

        return instance


    def __init__(self, request, *args, **kwargs):
        super(AtelierForm, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        listeChoix = [(u.id,u) for i, u in enumerate(Profil.objects.all().order_by('username'))]
        listeChoix.insert(0, (0, "----------------"))
        self.fields['referent'].choices = listeChoix
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]

class AtelierChangeForm(forms.ModelForm):
    referent = forms.ChoiceField(label='Référent(.e) atelier')

    class Meta:
        model = Atelier
        fields = [ 'titre', 'statut', 'asso', 'categorie', 'article', 'referent', 'description', 'materiel','start_time',  'heure_atelier', 'heure_atelier_fin', 'tarif_par_personne', 'estArchive' ]
        widgets = {
            'description': SummernoteWidget(),
            'materiel': SummernoteWidget(),
            'outils': SummernoteWidget(),
            'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'heure_atelier': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
            'duree_prevue': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
        }


    def __init__(self, *args, **kwargs):
        super(AtelierChangeForm, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        listeChoix = [(u.id,u) for i, u in enumerate(Profil.objects.all().order_by('username'))]
        listeChoix.insert(0, (0, kwargs["instance"].referent))
        self.fields['referent'].choices = listeChoix

    def save(self):
        instance = super(AtelierChangeForm, self).save(commit=False)
        try:
            referent = int(self.cleaned_data['referent'])
            instance.referent = dict(self.fields['referent'].choices)[referent].username
        except:
            instance.referent = dict(self.fields['referent'].choices)[referent]
            pass
        instance.save()
        return instance

class CommentaireAtelierForm(forms.ModelForm):

    class Meta:
        model = CommentaireAtelier
        exclude = ['atelier','auteur_comm']
        #
        widgets = {
          'commentaire': SummernoteWidgetWithCustomToolbar(),
        #        'commentaire': forms.Textarea(attrs={'rows': 1}),
           }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireAtelierForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False

class CommentaireAtelierChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = CommentaireAtelier
        exclude = ['atelier','auteur_comm']
        widgets = {
            'commentaire': SummernoteWidget(),
        }


class ContactParticipantsForm(forms.Form):
    msg = forms.CharField(label="Message", widget=SummernoteWidget)

