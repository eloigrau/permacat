from django import forms
from.models import InscriptionExposant
from django.http import HttpResponseRedirect
from formtools.preview import FormPreview

from django_summernote.widgets import SummernoteWidget

class InscriptionExposantForm(forms.ModelForm):
    nom_structure = forms.CharField(label="Nom de la structure, association, autre")
    procedure_lue = forms.BooleanField(label="J'ai lu et compris la procédure d'inscription (en haut de la page)", required=True)

    class Meta:
        model = InscriptionExposant
        fields = ['nom_structure', 'type_inscription', 'telephone', 'procedure_lue' ]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, request, message=None, *args, **kwargs):
        super(InscriptionExposantForm, self).__init__(request, *args, **kwargs)
        if message:
           self.fields['description'].initial = message