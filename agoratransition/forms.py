from django import forms
from.models import InscriptionExposant, Proposition, Message_agora
from django.core.mail import send_mail
from bourseLibre.settings.production import SERVER_EMAIL

from django_summernote.widgets import SummernoteWidget

LIST_EMAIL_SUIVI = ['eloi.grau@gmail.com']

class InscriptionForm(forms.ModelForm):
    #procedure_lue = forms.BooleanField(label="J'ai lu et compris la procédure d'inscription (en bas de la page)", required=True)

    class Meta:
        model = InscriptionExposant
        fields = ['nom', 'email', 'type_inscription', 'telephone', 'commentaire' ]
        widgets = {
            #'commentaire': SummernoteWidget(),
        }

    def __init__(self, request, message=None, *args, **kwargs):
        super(InscriptionForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['commentaire'].initial = message

    def save(self,):
        instance = super(InscriptionForm, self).save()
        envoyeur = self.cleaned_data["nom"] + ' (' +self.cleaned_data["email"]  + ')'
        sujet = self.cleaned_data['[AT] Nouvelle inscription']
        message_html = envoyeur + " s'est inscrit. Type : " + self.cleaned_data['type_inscription'] + ', tel:' + self.cleaned_data['telephone'] + ', commentaire : ' + self.cleaned_data['commentaire']
        send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

        return instance


class PropositionForm(forms.ModelForm):
    class Meta:
        model = Proposition
        fields = ['nom', "email", "telephone", 'proposition']
        widgets = {
           # 'proposition': SummernoteWidget(),
        }

    def __init__(self, request, message=None, *args, **kwargs):
        super(PropositionForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['description'].initial = message


    def save(self,):
        instance = super(InscriptionForm, self).save()
        envoyeur = self.cleaned_data["nom"] + ' (' +self.cleaned_data["email"]  + ')'
        sujet = self.cleaned_data['[AT] Nouvelle proposition']
        message_html = envoyeur + " a envoyé la proposition suivante : " + self.cleaned_data['proposition']
        send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

        return instance


class ContactForm(forms.ModelForm):

    class Meta:
        model = Message_agora
        fields = ['nom', "email", "msg"]
        widgets = {
         #   'msg': SummernoteWidget(),
        }

    def save(self,):
        instance = super(InscriptionForm, self).save()
        envoyeur = self.cleaned_data["nom"] + ' (' +self.cleaned_data["email"] + ')'
        sujet = self.cleaned_data['[AT] Nouveau message']
        message_html = envoyeur + " a envoyé un message " + self.cleaned_data['msg']
        send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

        return instance
    #email = forms.EmailField(label="Email")
    #nom = forms.CharField(max_length=250, label="Nom prénom / Raison sociale",)
    #msg = forms.CharField(label="Message", widget=SummernoteWidget)
