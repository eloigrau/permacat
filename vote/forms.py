from django import forms
from .models import Suffrage, Vote, Commentaire
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from blog.forms import SummernoteWidgetWithCustomToolbar
from django.utils.timezone import now
from bourseLibre.settings import LOCALL

class SuffrageForm(forms.ModelForm):
    estPublic = forms.ChoiceField(choices=((1, "Suffrage public"), (0, "Suffrage Permacat")), label='', required=True, )

    class Meta:
        model = Suffrage
        fields = ['type_vote', 'question', 'contenu',  'estAnonyme', 'start_time', 'end_time', 'estPublic']
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
        if not userProfile.is_permacat:
            instance.estPublic = True

        instance.save(userProfile)

        return instance


class SuffrageChangeForm(forms.ModelForm):
    estPublic = forms.ChoiceField(choices=((1, "Suffrage public"), (0, "Suffrage réservée aux adhérents")), label='', required=True)

    class Meta:
        model = Suffrage
        fields = ['type_vote', 'contenu', 'start_time', 'end_time', 'estAnonyme', 'estPublic', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'class':"date", }),
              'end_time': forms.DateInput(attrs={'class':'date', }),
        }

    def __init__(self, *args, **kwargs):
        super(SuffrageChangeForm, self).__init__(*args, **kwargs)
        self.fields["estPublic"].choices=((1, "Suffrage public"), (0, "Suffrage réservé aux adhérents")) if kwargs['instance'].estPublic else ((0, "Suffrage réservé aux adhérents"),(1, "Suffrage public"), )


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