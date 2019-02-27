from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, User
from .models import Produit, Produit_aliment, Produit_objet, Produit_service, Produit_vegetal, Adresse, Profil
from phonenumber_field.formfields import PhoneNumberField


#validateur:
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
#
# def validate_even(value):
#     if value % 2 != 0:
#         raise ValidationError(
#             _('%(value)s is not an even number'),
#             params={'value': value},
#         )
#
# class MyForm(forms.Form):
#     even_field = forms.IntegerField(validators=[validate_even])


fieldsCommunsProduits = ['nom_produit', 'souscategorie', 'photo', 'etat',   'description', 'estUneOffre',
                'prix',  'unite_prix', 'type_prix', 'date_debut', 'date_expiration', 'stock_initial',]

# fieldsCommunsProduits = ['type_prix', 'souscategorie', 'etat']
#
class ProduitCreationForm(forms.ModelForm):
    class Meta:
        model = Produit
        exclude=('user', )

        fields = ['nom_produit', 'photo','description', 'date_debut', 'date_expiration',
                  'stock_initial', 'unite_prix','prix',]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
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
class Produit_service_CreationForm(forms.ModelForm):
    class Meta:
        model = Produit_service
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
        }


class Produit_objet_CreationForm(forms.ModelForm):
    class Meta:
        model = Produit_objet
        fields = fieldsCommunsProduits
        widgets = {
            'date_debut': forms.DateInput(attrs={'type':"date"}, ),
            'date_expiration': forms.DateInput(attrs={'type':"date"})
        }

class AdresseForm(forms.ModelForm):
    rue = forms.CharField(label="Adresse", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000")
    telephone = forms.CharField(label="Téléphone", required=False)
    pays = forms.CharField(label="Pays", initial="France",required=False)
    latitude = forms.FloatField(label="Latitude", initial="42", required=False,widget = forms.HiddenInput())
    longitude = forms.FloatField(label="Longitude", initial="2", required=False,widget = forms.HiddenInput())

    class Meta:
        model = Adresse
        #fields = ('rue','code_postal','pays','telephone',)
        exclude = ('latitude', 'longitude')

    def save(self, *args, **kwargs):
        adresse = super(AdresseForm, self).save(commit=False)
        adresse.set_latlon_from_adresse()
        adresse.save()
        return adresse

class ProfilCreationForm(forms.ModelForm):
    class Meta:
        model = Profil
        exclude = ['user', 'adresse', 'slug']

    def save(self, commit = True):
        profil = super(ProfilCreationForm, self).save(commit)
        return profil


class ProducteurCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=False)
    username = forms.CharField(label="pseudonyme", required=True)
    name = forms.CharField(label="Nom complet", required=False)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2',
                #  'competences', 'rue', 'code_postal', 'latitude', 'longitude', 'pays', 'telephone'
                  ]
    #
    def save(self, commit=True, is_active = False):
        user = super(ProducteurCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username =self.cleaned_data['username']
        user.set_password(self.cleaned_data['password1'])
        user.is_active = is_active
        user.is_superuser = False

        if commit:
            user.save()
        return user

    # def save(self,):
    #     user = super(UserCreationForm, self).save(commit=False)
    #     user.email= self.cleaned_data['email']
    #     user.username=self.cleaned_data['username']
    #     user.password= self.cleaned_data['password1']
    #     user.is_active=False
    #     user.is_superuser=False
    #
    #     adresse =  Adresse.objects.create(
    #         rue=self.cleaned_data['rue'],
    #         code_postal=self.cleaned_data['code_postal'],
    #         latitude=self.cleaned_data['latitude'],
    #         longitude=self.cleaned_data['longitude'],
    #         pays=self.cleaned_data['pays'],
    #         telephone=self.cleaned_data['telephone'])
    #
    #     user.save()
    #     adresse.save()
    #     profil = Profil.objects.create(adresse=adresse,
    #                                    description=self.cleaned_data['description'],
    #                                    competences=self.cleaned_data['competences'])
    #
    #     #profil= super(ProfilCreationForm, self).save(commit=False)
    #     profil.user=user
    #     profil.adresse=adresse
    #     profil.description=self.cleaned_data['description']
    #     profil.competences=self.cleaned_data['competences']
    #     # profil = Profil.objects.create(user=user,
    #     #                                adresse=adresse,
    #     #                                description=self.cleaned_data['description'],
    #     #                                competences=self.cleaned_data['competences'])
    #
    #     profil.save()
    #
    #     return profil


    # def save(self, commit=True):
    #     user = super(ProducteurCreationForm, self).save(commit=False)
    #     user.email = self.cleaned_data['email']
    #     user.username = self.cleaned_data['username']
    #     user.description = self.cleaned_data['description']
    #     user.password = self.cleaned_data['password1']
    #
    #     if commit:
    #         user.save()
    #
    #     return user


class ProducteurChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Username")
    description = forms.CharField()
    competences = forms.CharField(label="competences")
    avatar = forms.ImageField(required=False)
    inscrit_newsletter = forms.BooleanField(required=False)

    def __init__(self, *args, **kargs):
        super(ProducteurChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
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