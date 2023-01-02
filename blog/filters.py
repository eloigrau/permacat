from django import forms
from bourseLibre.models import Asso, Profil
from .models import Article
import django_filters
from datetime import datetime, timedelta

class ArticleFilter(django_filters.FilterSet):
    asso = django_filters.ModelMultipleChoiceFilter(field_name='asso', queryset=Asso.objects.all(),
        widget=forms.CheckboxSelectMultiple)
    titre = django_filters.CharFilter(lookup_expr='icontains',)
    contenu = django_filters.CharFilter(lookup_expr='icontains', )
    estArchive = django_filters.BooleanFilter(field_name='estArchive', method='filtrer_archive')
    auteur = django_filters.ModelChoiceFilter(field_name='auteur', queryset=Profil.objects.all().extra(\
    select={'lower_name':'lower(username)'}).order_by('lower_name'), )
    #date_creation = django_filters.DateFromToRangeFilter(label="Date de création de l'article", widget=forms.DateInput(attrs={'class':"date", }))
    #start_time = django_filters.DateFromToRangeFilter(label="Date de l'evenement associé à l'article", widget=forms.DateInput(attrs={'class':"date", }))
    date_creation = django_filters.NumberFilter(
        field_name='date_creation', method='get_past_n_days', label="Articles créés depuis X jours")

    def filtrer_archive(self, queryset, field_name, value):
        return queryset.filter(estArchive=value)

    def get_past_n_days(self, queryset, field_name, value):
        time_threshold = datetime.now() - timedelta(days=int(value))
        return queryset.filter(date_creation__gte=time_threshold)

    class Meta:
        model = Article
        fields = {
            'categorie': ['exact', ],
            'titre': ['icontains', ],
            'contenu': ['icontains', ],
            'auteur': ['exact', ],
            "asso": ['exact', ],
            "estArchive": ['exact', ],
            #"start_time": ['range', ],
        }
