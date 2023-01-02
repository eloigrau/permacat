from django import forms
from bourseLibre.models import Asso, Profil
from .models import Document
import django_filters
from datetime import datetime, timedelta, timezone

class DocumentFilter(django_filters.FilterSet):
    asso = django_filters.ModelMultipleChoiceFilter(field_name='asso', queryset=Asso.objects.all(),
        widget=forms.CheckboxSelectMultiple)
    titre = django_filters.CharFilter(lookup_expr='icontains',)
    auteur = django_filters.ModelChoiceFilter(field_name='auteur', queryset=Profil.objects.all().extra(\
    select={'lower_name':'lower(username)'}).order_by('lower_name'), )
    #date_creation = django_filters.DateFromToRangeFilter(label="Date de création de l'article", widget=forms.DateInput(attrs={'class':"date", }))
    #start_time = django_filters.DateFromToRangeFilter(label="Date de l'evenement associé à l'article", widget=forms.DateInput(attrs={'class':"date", }))
    date_creation = django_filters.NumberFilter(
        field_name='date_creation', method='get_past_n_days', label="Documents créés depuis X jours")

    def get_past_n_days(self, queryset, field_name, value):
        time_threshold = datetime.now() - timedelta(days=int(value))
        return queryset.filter(date_creation__gte=time_threshold)

    class Meta:
        model = Document
        fields = {
            'titre': ['icontains', ],
            'auteur': ['exact', ],
            "asso": ['exact', ],
        }
