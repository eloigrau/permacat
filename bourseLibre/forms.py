from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, User
from .models import Produit, Produit_aliment, Produit_objet, Produit_service, Produit_vegetal, Adresse, Profil, Message, MessageGeneral
from captcha.fields import CaptchaField 

fieldsCommunsProduits = ['nom_produit', 'souscategorie',  'description', 'estUneOffre', 'estPublique',
                'unite_prix', 'prix',  'type_prix', 'date_debut', 'date_expiration', ]


class ProduitCreationForm(forms.ModelForm):
    class Meta:
        model = Produit
        exclude=('user', )

        fields = ['nom_produit', 'description', 'date_debut', 'date_expiration',
                  'stock_initial', 'unite_prix','prix',]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"}),
            'estUneOffre': forms.RadioSelect(choices=('oui', 'non')),
            'estPublique': forms.RadioSelect(choices=('oui', 'non')),
        }


class Produit_aliment_CreationForm(forms.ModelForm):
    class Meta:
        model = Produit_aliment
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
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

class Produit_vegetal_CreationForm(forms.ModelForm):
    class Meta:
        model = Produit_vegetal
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
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

class Produit_service_CreationForm(forms.ModelForm):
    class Meta:
        model = Produit_service
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
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


class Produit_objet_CreationForm(forms.ModelForm):
    class Meta:
        model = Produit_objet
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
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

class AdresseForm(forms.ModelForm):
    rue = forms.CharField(label="Adresse", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000")
    telephone = forms.CharField(label="Téléphone", required=False)
    pays = forms.CharField(label="Pays", initial="France",required=False)
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

    class Meta(UserCreationForm):
        model = Profil
        fields = ['username', 'password1',  'password2', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences', 'inscrit_newsletter', 'membre_permacat', 'accepter_conditions'
        exclude = ['adresse', 'slug']

    def save(self, commit = True, is_active=False):
        self.is_active=is_active

        return super(ProfilCreationForm, self).save(commit)


# class NewUserCreationForm(UserCreationForm):
#     email = forms.EmailField(label="Email", required=False)
#     username = forms.CharField(label="Pseudonyme*", required=True)
#     name = forms.CharField(label="Nom complet", required=False)
#
#     class Meta(UserCreationForm.Meta):
#         model = Profil
#         fields = ['name', 'username', 'email']
#
#     def save(self, commit=True, is_active = False):
#         user = super(NewUserCreationForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']
#         user.username =self.cleaned_data['username']
#         user.set_password(self.cleaned_data['password1'])
#         user.is_active = is_active
#         user.is_superuser = False
#
#         if commit:
#             user.save()
#         return user



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

    class Meta:
        model = Profil
        fields = ['username', 'email', 'description', 'competences', 'inscrit_newsletter']


class ContactForm(forms.Form):
    #envoyeur = forms.EmailField(label="Votre adresse mail")
    sujet = forms.CharField(max_length=100, )
    message = forms.CharField(widget=forms.Textarea, )
    renvoi = forms.BooleanField(label="recevoir une copie",
                                help_text="Cochez si vous souhaitez obtenir une copie du mail envoyé.", required=False
                                 )

    def __init__(self, request, envoyeur=None, message=None,  titre=None,  *args, **kwargs):
         super(ContactForm, self).__init__(request, *args, **kwargs)
         if envoyeur:
             self.fields['envoyeur'].initial = envoyeur
         if message:
             self.fields['message'].initial = message
         if titre:
             self.fields['sujet'].initial = titre

    # class UserForm(forms.ModelForm):
    #     class Meta:
    #         model = User
    #         fields = ('first_name', 'last_name', 'email')
    #
    # class ProfileForm(forms.ModelForm):
    #     class Meta:
    #         model = Profil
    #         fields = ('site_web', 'description', 'avatar', 'inscrit_newsletter')

    # class ConnexionForm(forms.Form):
    #     username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    #     password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

#
# from .models import Place
#
#
# class LocationForm(forms.ModelForm):
#     class Meta:
#         model = Place
#         exclude = ()


# class FiltreForm(forms.Form):
#     demande = forms.ChoiceField(
#         choices=(('tout','tout'),('offres','offres'),('recherches','recherches')),
#     )



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

class MessageGeneralForm(forms.ModelForm):

    class Meta:
        model = MessageGeneral
        exclude = ['auteur']

        widgets = {
                'message': forms.Textarea(attrs={'rows': 1}),
            }

