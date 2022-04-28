from django import forms
from.models import InscriptionExposant, Proposition, Message_agora
from django.core.mail import send_mail
from bourseLibre.settings.production import SERVER_EMAIL, LOCALL
from .envoi_mail import envoyerMailPermAgora
#from django_summernote.widgets import SummernoteWidget

LIST_EMAIL_SUIVI = ['eloi.grau@gmail.com', "permagora66@gmail.com", ]

class InscriptionForm(forms.ModelForm):
    #procedure_lue = forms.BooleanField(label="J'ai lu et compris la procédure d'inscription (en bas de la page)", required=True)

    class Meta:
        model = InscriptionExposant
        fields = ['nom', 'email', 'type_inscription', 'telephone', 'commentaire']
        widgets = {
            #'commentaire': SummernoteWidget(),
        }

    def __init__(self, request, message=None, *args, **kwargs):
        super(InscriptionForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['commentaire'].initial = message

    def save(self,):
        instance = super(InscriptionForm, self).save()
        if not LOCALL:
            envoyeur = self.cleaned_data["nom"] + ' (' + self.cleaned_data["email"] + ')'
            sujet = '[AgoraTransition] Nouvelle inscription'
            message_html = envoyeur + " s'est inscrit.e Type : " + self.cleaned_data['type_inscription'] + ', tel:' + self.cleaned_data['telephone'] + ', commentaire : ' + self.cleaned_data['commentaire']
            send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

            sujet = '[AgoraTransition] inscription'
            message_html = " <div> \
<p>Bonjour,</p>\
</div>\
<div>Merci pour votre inscription &agrave; la <a href='https://www.perma.cat/agoratransition/'>Journ&eacute;e de la Transition !</a></div>\
<div>&nbsp;</div>\
<div>Nous souhaitons laisser la possibilit&eacute; d'une coop&eacute;ration pour l'organisation de cette journ&eacute;e. Pour cela, merci de répondre au  <a href='https://framaforms.org/tables-rondes-de-la-premiere-agora-de-la-transition-du-8-mai-2022-1650658357'>questionnaire suivant</a></div>\
<div>&nbsp;</div>\
<div>Pour toute information compl&eacute;mentaire, nous nous tenons &agrave; votre disposition.</div>\
<div>&nbsp;</div>\
<div>Fins aviat !</div>\
<div>&nbsp;</div>\
<div>Cathy (06.62.64.31.59), Eloi et Anna </div>\
<div>Mail : permagora66@gmail.com</div>"
            envoyerMailPermAgora(sujet, message_html, [self.cleaned_data["email"], ])
            #send_mail(sujet, message_html,  SERVER_EMAIL, [self.cleaned_data["email"], ], fail_silently=False, html_message=message_html)

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
        instance = super(PropositionForm, self).save()
        if not LOCALL:
            envoyeur = self.cleaned_data["nom"] + ' (' + self.cleaned_data["email"] + ')'
            sujet = '[AgoraTransition] Nouvelle proposition'
            message_html = envoyeur + " a envoyé la proposition suivante : " + self.cleaned_data['proposition']
            send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

        return instance

class ContactForm(forms.ModelForm):

    class Meta:
        model = Message_agora
        fields = ['nom', "email", "msg"]
        widgets = {
            # 'msg': SummernoteWidget(),
        }

    def save(self,):
        instance = super(ContactForm, self).save()
        if not LOCALL:
            envoyeur = self.cleaned_data["nom"] + ' (' + self.cleaned_data["email"] + ')'
            sujet = '[AgoraTransition] Nouveau message'
            message_html = envoyeur + " a envoyé un message " + self.cleaned_data['msg']
            send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

        return instance

    #email = forms.EmailField(label="Email")
    #nom = forms.CharField(max_length=250, label="Nom prénom / Raison sociale",)
    #msg = forms.CharField(label="Message", widget=SummernoteWidget)