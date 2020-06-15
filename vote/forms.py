from django import forms
from .models import Votation, Vote, Commentaire
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget
from blog.forms import SummernoteWidgetWithCustomToolbar



class VotationForm(forms.ModelForm):
    estPublic = forms.ChoiceField(choices=((1, "Votation publique"), (0, "Votation Permacat")), label='', required=True, )

    class Meta:
        model = Votation
        fields = ['type_vote', 'titre', 'contenu',  'question', 'estAnonyme', 'start_time', 'end_time', 'estPublic']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'type': 'date'}),
              'end_time': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, userProfile):
        instance = super(VotationForm, self).save(commit=False)

        max_length = Votation._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Votation.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile
        if not userProfile.is_permacat:
            instance.estPublic = True

        instance.save()

        return instance


class VotationChangeForm(forms.ModelForm):
    estPublic = forms.ChoiceField(choices=((1, "Votation publique"), (0, "Votation réservée aux adhérents")), label='', required=True)

    class Meta:
        model = Votation
        fields = ['type_vote', 'titre', 'contenu', 'start_time', 'end_time', 'estAnonyme', 'estPublic', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time': forms.DateInput(attrs={'class':"date", }),
              'end_time': forms.DateInput(attrs={'class':'date', }),
        }

    def __init__(self, *args, **kwargs):
        super(VotationChangeForm, self).__init__(*args, **kwargs)
        self.fields["estPublic"].choices=((1, "Votation public"), (0, "Votation réservé aux adhérents")) if kwargs['instance'].estPublic else ((0, "Votation réservé aux adhérents"),(1, "Votation public"), )

class CommentaireVotationForm(forms.ModelForm):

    class Meta:
        model = Commentaire
        exclude = ['votation', 'auteur_comm']
        #
        widgets = {
         'commentaire': SummernoteWidgetWithCustomToolbar(),
               # 'commentaire': forms.Textarea(attrs={'rows': 1}),
            }

    def __init__(self, request, *args, **kwargs):
        super(CommentaireVotationForm, self).__init__(request, *args, **kwargs)
        self.fields['commentaire'].strip = False



class CommentaireVotationChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
     model = Commentaire
     exclude = ['votation', 'auteur_comm']


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        exclude = ['votation','auteur']

    def save(self, votation, userProfile):
        instance = super(VoteForm, self).save(commit=False)
        instance.auteur = userProfile
        instance.votation = votation
        instance.save()
        return instance

class VoteChangeForm(forms.ModelForm):
    class Meta:
        model = Vote
        exclude = ['votation','auteur']




class CommentaireVotationChangeForm(forms.ModelForm):
    commentaire = forms.CharField(required=False, widget=SummernoteWidget(attrs={}))

    class Meta:
     model = Commentaire
     exclude = ['votation', 'auteur_comm']