from django import forms
from bourseLibre.models import Asso, Profil
import django_filters
from django.db.models import Q

class ProfilCarteFilter(django_filters.FilterSet):
    adherent_pc = django_filters.BooleanFilter(field_name='adherent_pc', method='get_adherent_asso',
                                               label="Membre de PermaCat")
    adherent_scic = django_filters.BooleanFilter(field_name='adherent_scic', method='get_adherent_asso',
                                                  label="Membre de PermAgora")
    adherent_rtg = django_filters.BooleanFilter(field_name='adherent_rtg', method='get_adherent_asso',
                                                  label="Membre de Ramène Ta Graine")
    adherent_citealt = django_filters.BooleanFilter(field_name='adherent_citealt', method='get_adherent_asso',
                                                  label="Membre de la Cité Altruiste")
    compet_descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_competencedesritpion_filter', label="Mot dans la compétence ou la description")



    def get_adherent_asso(self, queryset, field_name, value):
        return queryset.filter(**{field_name: value})
    def get_competencedesritpion_filter(self, queryset, field_name, value):
        return queryset.filter(Q(description__icontains=value)|Q(competences__icontains=value))

    class Meta:
        model = Profil
        fields = {
            'compet_descrip': ['icontains', ],
            "adherent_pc": ['exact', ],
            "adherent_scic": ['exact', ],
            "adherent_rtg": ['exact', ],
            "adherent_citealt": ['exact', ],
        }