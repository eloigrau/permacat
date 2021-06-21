from django import forms
from bourseLibre.models import Asso, Profil
from .models import Article, Choix
from django_filters.views import FilterView
import django_filters
from django_summernote.widgets import SummernoteWidget
from photologue.models import Album
from bourseLibre.constantes import Choix as Choix_global

class ArticleFilter(django_filters.FilterSet):
    asso = django_filters.ModelMultipleChoiceFilter(field_name='asso', queryset=Asso.objects.all().exclude(abreviation="jp"),
        widget=forms.CheckboxSelectMultiple)
    titre = django_filters.CharFilter(lookup_expr='icontains',)
    contenu = django_filters.CharFilter(lookup_expr='icontains', )
    auteur = django_filters.ModelChoiceFilter(field_name='auteur', queryset=Profil.objects.all().order_by('username'),
        )

    class Meta:
        model = Article
        fields = {
            'categorie': ['exact', ],
            'titre': ['icontains', ],
            'contenu': ['icontains', ],
            'auteur': ['exact', ],
            "asso": ['exact', ],
        }
    #
    # @property
    # def qs(self):
    #     parent = super().qs
    #     user = getattr(self.request, 'user', None)
    #
    #     for nomAsso in Choix_global.abreviationsAsso:
    #         if not getattr(user, "adherent_" + nomAsso):
    #             parent = parent.exclude(asso__abreviation=nomAsso)
    #     return parent
