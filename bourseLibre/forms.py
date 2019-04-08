from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Produit, Produit_aliment, Produit_objet, Produit_service, Produit_vegetal, Adresse, Profil, Message, MessageGeneral, Choix
from captcha.fields import CaptchaField

fieldsCommunsProduits = ['nom_produit', 'souscategorie',  'description', 'estUneOffre', 'estPublique',
                'unite_prix', 'prix',  'type_prix', 'date_debut', 'date_expiration', ]


class ProduitCreationForm(forms.ModelForm):
    estUneOffre = forms.ChoiceField(choices=((1, "Offre"), (0, "Demande")), label='', required=True)
    estPublique = forms.ChoiceField(choices=((1, "Annonce publique"), (0, "Annonce réservée aux adhérents")), label='', required=True)

    class Meta:
        model = Produit
        exclude=('user', )

        fields = ['nom_produit', 'description', 'date_debut', 'date_expiration',
                  'stock_initial', 'unite_prix','prix',]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"}),
        }


    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_expiration = cleaned_data.get("date_expiration")
        if date_debut and date_expiration:
            # Only do something if both fields are valid so far.
            if date_debut > date_expiration:
                raise forms.ValidationError(
                    "La date de fin doit etre après la date de début"
                )
        return self.cleaned_data

class Produit_aliment_CreationForm(ProduitCreationForm):

    class Meta:
        model = Produit_aliment
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"}),
        }


class Produit_vegetal_CreationForm(ProduitCreationForm):

    class Meta:
        model = Produit_vegetal
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"}),
            #'estUneOffre': forms.RadioSelect(choices=('oui', 'non')),
            #'estPublique': forms.RadioSelect(choices=('oui', 'non')),
        }

class Produit_service_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_service
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"}),
          #  'estUneOffre': forms.RadioSelect(choices=('oui', 'non')),
           # 'estPublique': forms.RadioSelect(choices=('oui', 'non')),
        }
class Produit_objet_CreationForm(ProduitCreationForm):
    class Meta:
        model = Produit_objet
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
        }

class AdresseForm(forms.ModelForm):
    rue = forms.CharField(label="Rue*", required=True)
    code_postal = forms.CharField(label="Code postal*", initial="66000")
    telephone = forms.CharField(label="Téléphone*", required=True)
    pays = forms.CharField(label="Pays*", initial="France",required=True)
    latitude = forms.FloatField(label="Latitude", initial="42", required=False,widget = forms.HiddenInput())
    longitude = forms.FloatField(label="Longitude", initial="2", required=False,widget = forms.HiddenInput())

    class Meta:
        model = Adresse
        exclude = ('latitude', 'longitude')

    def save(self, *args, **kwargs):
        adresse = super(AdresseForm, self).save(commit=False)
        adresse.set_latlon_from_adresse()
        adresse.save()
        return adresse

class ProfilCreationForm(UserCreationForm):
    username = forms.CharField(label="Pseudonyme*", help_text="Attention les majuscules sont importantes...")
    description = forms.CharField(label="Description*", help_text="Une description de vous même", widget=forms.Textarea)
    competences = forms.CharField(label="Savoir-faire*", help_text="Par exemple: electricien, bouturage, aromatherapie, etc...", widget=forms.Textarea)
    site_web = forms.CharField(label="Site web", help_text="n'oubliez pas le https://", required=False)
    captcha = CaptchaField()

    statut_adhesion = forms.ChoiceField(choices=Choix.statut_adhesion, label='', required=True)
    accepter_conditions = forms.BooleanField(required=True, label="J'ai lu et j'accepte les Conditions Générales d'Utilisation du site",  )
    pseudo_june = forms.CharField(label="Pseudonyme dans la monnaie libre (Duniter)",  help_text="Si vous avez un compte en June",required=False)


    def __init__(self, request, *args, **kargs):
        super(ProfilCreationForm, self).__init__(request, *args, **kargs)
        self.fields['description'].strip = False
        self.fields['competences'].strip = False

    class Meta(UserCreationForm):
        model = Profil
        fields = ['username', 'password1',  'password2', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences', 'pseudo_june', 'inscrit_newsletter', 'accepter_annuaire', 'statut_adhesion', 'accepter_conditions']
        exclude = ['slug', ]

    def save(self, commit = True, is_active=False):
        self.is_active=is_active

        return super(ProfilCreationForm, self).save(commit)


class ProducteurChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Pseudonyme")
    description = forms.CharField(label="Description", initial="Une description de vous même", widget=forms.Textarea)
    competences = forms.CharField(label="Savoir-faire", initial="Par exemple: electricien, bouturage, aromatherapie, etc...",widget=forms.Textarea)
    avatar = forms.ImageField(required=False)
    inscrit_newsletter = forms.BooleanField(required=False)
    password=None

    def __init__(self, *args, **kargs):
        super(ProducteurChangeForm, self).__init__(*args, **kargs)
        self.fields['description'].strip = False
        self.fields['competences'].strip = False

    class Meta:
        model = Profil
        fields = ['username', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences', 'pseudo_june', 'inscrit_newsletter', 'accepter_annuaire']


class ProducteurChangeForm_admin(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Pseudonyme")
    description = forms.CharField(label="Description", initial="Une description de vous même", widget=forms.Textarea)
    competences = forms.CharField(label="Savoir-faire",
                                  initial="Par exemple: electricien, bouturage, aromatherapie, etc...", required=False,
                                  widget=forms.Textarea)
    avatar = forms.ImageField(required=False)
    inscrit_newsletter = forms.BooleanField(required=False)
    pseudo_june = forms.CharField(label="pseudo_june",required=False)

    statut_adhesion = forms.ChoiceField(choices=Choix.statut_adhesion)
    password = None

    class Meta:
        model = Profil
        fields = ['username', 'email', 'description', 'competences', 'inscrit_newsletter', 'statut_adhesion', 'pseudo_june', ]

    def __init__(self, *args, **kwargs):
        super(ProducteurChangeForm_admin, self).__init__(*args, **kwargs)
        self.fields['description'].strip = False
        self.fields['competences'].strip = False

class ContactForm(forms.Form):
    sujet = forms.CharField(max_length=100, )
    message = forms.CharField(widget=forms.Textarea, )
    renvoi = forms.BooleanField(label="recevoir une copie",
                                help_text="Cochez si vous souhaitez obtenir une copie du mail envoyé.", required=False
                                 )

    def __init__(self, message=None,  titre=None,  *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        if message:
            self.fields['message'].initial = message
        if titre:
            self.fields['sujet'].initial = titre
        self.fields['message'].strip = False


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        exclude = ['conversation','auteur']

        widgets = {
                'message': forms.Textarea(attrs={'rows': 2}),
            }

    def __init__(self, request, message=None, *args, **kwargs):
        super(MessageForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['message'].initial = message
        self.fields['message'].strip = False

class MessageGeneralForm(forms.ModelForm):

    class Meta:
        model = MessageGeneral
        exclude = ['auteur']

        widgets = {
                'message': forms.Textarea(attrs={'rows': 1}),
            }


    def __init__(self, request, message=None, *args, **kwargs):
        super(MessageGeneralForm, self).__init__(request, *args, **kwargs)
        self.fields['message'].strip = False