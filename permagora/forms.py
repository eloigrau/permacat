from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profil, Message_permagora, Choix, Commentaire_charte, PropositionCharte, PoleCharte
from captcha.fields import CaptchaField
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
import itertools
from django.utils.text import slugify
import re

no_space_validator = RegexValidator(
      r' ',
      ("Le pseudonyme ne doit pas contenir d'espaces"),
      inverse_match=True,
      code='invalid_tag',
  )
#
# class ProfilCreationForm(UserCreationForm):
#     username = forms.CharField(label="Pseudonyme*", help_text="Attention les majuscules sont importantes...", validators=[no_space_validator,])
#     description = forms.CharField(label=None, help_text="Une description de vous même", required=False, widget=forms.Textarea)
#     captcha = CaptchaField()
#     email= forms.EmailField(label="Email*",)
#     accepter_annuaire = forms.BooleanField(required=False, label="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous les inscrits")
#     accepter_conditions = forms.BooleanField(required=True, label="J'ai lu et j'accepte les Conditions Générales d'Utilisation du site",  )
#
#     class Meta(UserCreationForm):
#         model = Profil
#         fields = ['username', 'password1',  'password2', 'first_name', 'last_name', 'email',  'description', 'inscrit_newsletter', 'accepter_annuaire', 'accepter_conditions']
#         exclude = ['slug', ]
#
#     def save(self, commit = True, is_active=False):
#         return super(ProfilCreationForm, self).save(commit)
#         self.is_active=is_active
#
#
# class ProfilChangeForm_admin(UserChangeForm):
#     """A form for updating users. Includes all the fields on
#     the user, but replaces the password field with admin's
#     password hash display field.
#     """
#     email = forms.EmailField(label="Email")
#     username = forms.CharField(label="Pseudonyme", validators=[no_space_validator,])
#     description = forms.CharField(label="Description", initial="Une description de vous même (facultatif)", widget=forms.Textarea)
#     inscrit_newsletter = forms.BooleanField(required=False)
#     accepter_annuaire = forms.BooleanField(required=False)
#     a_signe = forms.BooleanField(required=False)
#     password = None
#
#     class Meta:
#         model = Profil
#         fields = ['username', 'email', 'description', 'inscrit_newsletter', 'accepter_annuaire', ]
#
#     def __init__(self, *args, **kwargs):
#         super(ProfilChangeForm_admin, self).__init__(*args, **kwargs)


class ContactForm(forms.Form):
    sujet = forms.CharField(max_length=100, label="Sujet",)
    msg = forms.CharField(label="Message")
    renvoi = forms.BooleanField(label="recevoir une copie",
                                     help_text="Cochez si vous souhaitez obtenir une copie du mail envoyé.", required=False
                                 )

    class Meta:
        widgets = {
                'msg': SummernoteWidget(),
            }

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message_permagora
        exclude = ['auteur', 'date_creation', 'type_article', 'type_message', 'valide']

        widgets = {
            'message': SummernoteWidget(),
            }

    def __init__(self, request, message=None, *args, **kwargs):
        super(MessageForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['message'].initial = message



class CommentaireForm(forms.ModelForm):

    class Meta:
        model = Commentaire_charte
        exclude = ['auteur', 'date_creation', 'type_message', 'valide', 'proposition']

        widgets = {
            'message': SummernoteWidget(),
            }

    def __init__(self, request, message=None, *args, **kwargs):
        super(CommentaireForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['message'].initial = message


class SignerForm(forms.Form):
    accepter = forms.BooleanField(label="Je soutiens les propositions de PermAgora et je m'engage avec le collectif", required=True)
    apparait_visible = forms.BooleanField(label="J'accepte que mon nom apparaisse sur la liste des soutiens", required=False)




class PropositionCharteCreationForm(forms.ModelForm):

    class Meta:
        model = PropositionCharte
        fields = ['pole', 'titre', 'ressources', 'contexte',  'ideal', 'existant', 'besoins', 'actions', ]
        widgets = {
            'ressources': SummernoteWidget(),
            'contexte': SummernoteWidget(),
            'besoins': SummernoteWidget(),
            'ideal': SummernoteWidget(),
            'existant': SummernoteWidget(),
            'actions': SummernoteWidget(),
        }

    def save(self, userProfile, sendMail=True):
        instance = super(PropositionCharteCreationForm, self).save(commit=False)

        max_length = PropositionCharte._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        x = 1
        while PropositionCharte.objects.filter(slug=instance.slug).exists():
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
            x += 1

        if len(re.findall(r"[A-Z]", instance.titre)) > 7:
            instance.titre = instance.titre.title()
        instance.auteur = userProfile

        instance.save()

        return instance

    def __init__(self, request, *args, **kwargs):
        super(PropositionCharteCreationForm, self).__init__(*args, **kwargs)


class PropositionCharteChangeForm(forms.ModelForm):

    class Meta:
        model = PropositionCharte
        fields = ['pole', 'titre', 'ressources', 'contexte', 'ideal', 'existant', 'besoins', 'actions',]
        widgets = {
            'ressources': SummernoteWidget(),
            'contexte': SummernoteWidget(),
            'besoins': SummernoteWidget(),
            'ideal': SummernoteWidget(),
            'existant': SummernoteWidget(),
            'actions': SummernoteWidget(),
        }

    def save(self, sendMail=True, commit=True):
        return super(PropositionCharteChangeForm, self).save(commit=commit)
