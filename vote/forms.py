from django import forms
from .models import Suffrage, Vote, Commentaire, Question_majoritaire, Question_binaire, ReponseQuestion_b, ReponseQuestion_m, \
    Proposition_m, Choix
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from blog.forms import SummernoteWidgetWithCustomToolbar
from bourseLibre.settings import LOCALL
from bourseLibre.models import Asso
from django.forms import formset_factory, BaseFormSet
from django.utils.timezone import now
from datetime import timedelta

class SuffrageForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().all(), required=True, label="Suffrage public ou réservé aux adhérents de l'asso :",)

    class Meta:
        model = Suffrage
        fields = ['asso', 'type_vote', 'titre', 'description', 'estAnonyme', 'start_time', 'end_time']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("start_time")
        date_expiration = cleaned_data.get("end_time")
        if date_debut < now().date() + timedelta(days=1):
            raise forms.ValidationError('Le suffrage ne peut pas démarrer avant demain')

        if date_expiration <= date_debut:
            raise forms.ValidationError('La date de fin doit etre postérieure à la date de début')

        return self.cleaned_data

    def save(self, userProfile, article):
        instance = super(SuffrageForm, self).save(commit=False)

        max_length = Suffrage._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Suffrage.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile
        instance.article = article

        instance.save(userProfile)

        return instance


class SuffrageChangeForm(forms.ModelForm):

    class Meta:
        model = Suffrage
        fields = [ 'asso', 'type_vote', 'titre', 'description', 'start_time', 'end_time', 'estAnonyme',  'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
              'end_time': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
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
            #if date_debut < now():
             #   raise forms.ValidationError('Le suffrage ne peut pas démarrer avant demain')

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
        self.fields['commentaire'].required = False


class Question_binaire_Form(forms.ModelForm):
    question = forms.CharField(required=True, max_length=150, help_text='Question qui sera soumise au vote, et dont la réponse pourra etre oui/non/ne se prononce pas', label='Question')

    class Meta:
        model = Question_binaire
        fields = ['question']

    def save(self, suffrage):
        instance = super(Question_binaire_Form, self).save(commit=False)
        instance.suffrage = suffrage
        instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question'].required = True


class Question_majoritaire_Form(forms.ModelForm):
    question = forms.CharField(required=True, max_length=150, help_text='Question soumise au vote par jugement majoritaire (classement des propositions)', label='Question "majoritaire". Par exemple "qui veut etre président" ?')

    class Meta:
        model = Question_majoritaire
        fields = [ 'question', 'type_choix',]

    def save(self, suffrage):
        instance = super(Question_majoritaire_Form, self).save(commit=False)
        instance.suffrage = suffrage
        instance.save()
        return instance

class Proposition_m_Form(forms.ModelForm):
    proposition = forms.CharField(required=True, max_length=150, help_text='Propostion de réponse à la question posée (candidature)', label='Proposition (candidat). Par exemple "Jean Luc"' )

    class Meta:
        model = Proposition_m
        fields = ['proposition']

    def save(self, question_m):
        instance = super(Proposition_m_Form, self).save(commit=False)
        instance.save(question_m)
        return instance

class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


Question_binaire_formset = formset_factory(Question_binaire_Form, formset=RequiredFormSet, extra=1, can_delete=False)
Proposition_m_formset = formset_factory(Proposition_m_Form, formset=RequiredFormSet, extra=0, can_delete=False)
Question_majoritaire_formset = formset_factory(Question_majoritaire_Form, extra=0, can_delete=False)


class Reponse_majoritaire_Form(forms.ModelForm):
    class Meta:
        model = ReponseQuestion_m
        fields = ['choix']

    def __init__(self, proposition, *args, **kwargs):
        super(Reponse_majoritaire_Form, self).__init__(*args, **kwargs)
        self.proposition = proposition
        self.question = proposition.question_m.question
        self.fields['choix'] = forms.ChoiceField(choices=Choix.vote_majoritaire[proposition.question_m.type_choix], label="-> " + proposition.proposition)

    def save(self, vote):
        instance = super(Reponse_majoritaire_Form, self).save(commit=False)
        instance.vote = vote
        instance.proposition = self.proposition
        instance.save()
        return instance

class Reponse_binaire_Form(forms.ModelForm):
    class Meta:
        model = ReponseQuestion_b
        fields = ['choix']

    def __init__(self, question, *args, **kwargs):
        super(Reponse_binaire_Form, self).__init__(*args, **kwargs)
        self.question = question
        self.fields['choix'].label = question.question


    def save(self, vote):
        instance = super(Reponse_binaire_Form, self).save(commit=False)
        instance.vote = vote
        instance.question = self.question
        instance.save()
        return instance

class CommentaireSuffrageChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = Commentaire
        exclude = ['suffrage', 'auteur_comm']
        widgets = {
            'commentaire': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commentaire'].required = False


class VoteForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
        model = Vote
        exclude = ['suffrage','auteur']
        widgets = {
            'commentaire': SummernoteWidget(),
        }

    def save(self, suffrage, userProfile):
        instance = super(VoteForm, self).save(commit=False)
        instance.suffrage = suffrage
        instance.auteur = userProfile
        instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commentaire'].required = False

class VoteChangeForm(forms.ModelForm):
    class Meta:
        model = Vote
        exclude = ['suffrage','auteur']
        widgets = {
            'commentaire': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commentaire'].required = False
