from django import forms
from.models import InscriptionExposant, Proposition, Message_agora

from django_summernote.widgets import SummernoteWidget

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
           self.fields['description'].initial = message



class PropositionForm(forms.ModelForm):
    class Meta:
        model = Proposition
        fields = ['nom', "email", "telephone", 'proposition', 'animeParProposant']
        widgets = {
           # 'proposition': SummernoteWidget(),
        }

    def __init__(self, request, message=None, *args, **kwargs):
        super(PropositionForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['description'].initial = message




class ContactForm(forms.ModelForm):

    class Meta:
        model = Message_agora
        fields = ['nom', "email", "msg"]
        widgets = {
         #   'msg': SummernoteWidget(),
        }
    #email = forms.EmailField(label="Email")
    #nom = forms.CharField(max_length=250, label="Nom prénom / Raison sociale",)
    #msg = forms.CharField(label="Message", widget=SummernoteWidget)
