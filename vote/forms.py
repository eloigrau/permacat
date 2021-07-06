from django import forms
from .models import Suffrage, Vote, Commentaire
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from blog.forms import SummernoteWidgetWithCustomToolbar
from django.utils.timezone import now
from bourseLibre.settings import LOCALL
from bourseLibre.models import Asso
from django.forms import formset_factory

class SuffrageForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True, label="Suffrage public ou réservé aux adhérents de l'asso :",)

    class Meta:
        model = Suffrage
        fields = ['type_vote', 'asso', 'question', 'contenu',  'estAnonyme', 'start_time', 'end_time']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'type': 'date'}),
              'end_time': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("start_time")
        date_expiration = cleaned_data.get("end_time")
        if date_debut < now():
            raise forms.ValidationError('Le suffrage ne peut pas démarrer avant demain')

        if date_expiration <= date_debut:
            raise forms.ValidationError('La date de fin doit etre postérieure à la date de début')

        return self.cleaned_data

    def save(self, userProfile):
        instance = super(SuffrageForm, self).save(commit=False)

        max_length = Suffrage._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.question)[:max_length]

        for x in itertools.count(1):
            if not Suffrage.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        instance.save(userProfile)

        return instance

SuffrageFormset = formset_factory(SuffrageForm, extra=1)

class SuffrageChangeForm(forms.ModelForm):

    class Meta:
        model = Suffrage
        fields = ['type_vote', 'asso', 'contenu', 'start_time', 'end_time', 'estAnonyme',  'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'class':"date", }),
              'end_time': forms.DateInput(attrs={'class':'date', }),
        }

    def save(self, userProfile):
        instance = super(SuffrageChangeForm, self).save(commit=False)
        instance.save(userProfile)
        return instance

    def clean(self):
        if not LOCALL:
            cleaned_data = super().clean()
            date_debut = cleaned_data.get("start_time")
            date_expiration = cleaned_data.get("end_time")
            if date_debut < now():
                raise forms.ValidationError('Le suffrage ne peut pas démarrer avant demain')

            if date_expiration <= date_debut:
                raise forms.ValidationError('La date de fin doit etre postérieure à la date de début')

        return self.cleaned_data

class CommentaireSuffrageForm(forms.ModelForm):

    class Meta:
        model = Commentaire
        exclude = ['suffrage', 'auteur_comm']
        widgets = {
         'commentaire': SummernoteWidgetWithCustomToolbar(),
               # 'commentaire': forms.Textarea(attrs={'rows': 1}),
            }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireSuffrageForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False



class CommentaireSuffrageChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = Commentaire
        exclude = ['suffrage', 'auteur_comm']
        widgets = {
            'commentaire': SummernoteWidget(),
        }


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        exclude = ['suffrage','auteur']
        widgets = {
            'commentaire': SummernoteWidget(),
        }

    def save(self, suffrage, userProfile):
        instance = super(VoteForm, self).save(commit=False)
        instance.suffrage = suffrage
        if not instance.suffrage.estAnonyme:
            instance.auteur = userProfile
        instance.save()
        return instance

class VoteChangeForm(forms.ModelForm):
    class Meta:
        model = Vote
        exclude = ['suffrage','auteur']
        widgets = {
            'commentaire': SummernoteWidget(),
        }


class CommentaireSuffrageChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = Commentaire
        exclude = ['suffrage', 'auteur_comm']
        widgets = {
            'commentaire': SummernoteWidget(),
            }