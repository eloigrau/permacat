from django import forms
from .models import Atelier, CommentaireAtelier, Atelier, InscriptionAtelier
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from bourseLibre.models import Profil
from blog.forms import SummernoteWidgetWithCustomToolbar
from bourseLibre.models import Asso

class AtelierForm(forms.ModelForm):
    referent = forms.ChoiceField(label='Référent atelier')
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                                  label="Atelier public ou réservé aux adhérents de l'asso :", )

    class Meta:
        model = Atelier
        fields = ['titre', 'statut', 'categorie', 'asso', 'referent', 'description', 'materiel', 'date_atelier','heure_atelier','duree_prevue', 'tarif_par_personne']
        widgets = {
            'description': SummernoteWidget(),
            'materiel': SummernoteWidget(),
            'date_atelier': forms.DateInput(attrs={'type':"date"}),
            'heure_atelier': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
            'duree_prevue': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
        }

    def save(self, request):
        instance = super(AtelierForm, self).save(commit=False)
        referent = self.cleaned_data['referent']
        try:
            instance.referent = dict(self.fields['referent'].choices)[referent]
        except:
            pass


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
            instance.save_m2m()
        except:
            pass

        return instance


    def __init__(self, request, *args, **kwargs):
        super(AtelierForm, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        listeChoix = [(i+1,u) for i, u in enumerate(Profil.objects.all().order_by('username'))]
        listeChoix.insert(0, (0, "----------------"))
        self.fields['referent'].choices = listeChoix
        self.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all()) if request.user.estMembre_str(x.abreviation)]

class AtelierChangeForm(forms.ModelForm):
    referent = forms.ChoiceField(label='Référent(.e) atelier')

    class Meta:
        model = Atelier
        fields = [ 'titre', 'statut', 'asso', 'categorie','referent', 'description', 'materiel','date_atelier',  'heure_atelier', 'duree_prevue', 'tarif_par_personne', ]
        widgets = {
            'description': SummernoteWidget(),
            'materiel': SummernoteWidget(),
            'outils': SummernoteWidget(),
            'date_atelier': forms.DateInput(),
            'heure_atelier': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
            'duree_prevue': forms.TimeInput(attrs={'type':"time", },format='%H:%M'),
        }


    def __init__(self, *args, **kwargs):
        super(AtelierChangeForm, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        listeChoix = [(i+1,u) for i, u in enumerate(Profil.objects.all().order_by('username'))]
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
