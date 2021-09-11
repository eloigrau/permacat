from django import forms
from bourseLibre.models import Asso, Profil
import django_filters


class ProfilCarteFilter(django_filters.FilterSet):
    adherent_pc = django_filters.BooleanFilter(field_name='adherent_pc', method='get_adherent_asso',
                                               label="PermaCat")
    adherent_scic = django_filters.BooleanFilter(field_name='adherent_scic', method='get_adherent_asso',
                                                  label="PermAgora")
    adherent_rtg = django_filters.BooleanFilter(field_name='adherent_rtg', method='get_adherent_asso',
                                                  label="Ramène Ta Graine")
    adherent_citealt = django_filters.BooleanFilter(field_name='adherent_citealt', method='get_adherent_asso',
                                                  label="Cité Altruiste")
    competences = django_filters.CharFilter(lookup_expr='icontains',  label="Mot dans la compétence")
    description = django_filters.CharFilter(lookup_expr='icontains',  label="Mot dans la description" )


    def get_adherent_asso(self, queryset, field_name, value):
        return queryset.filter(**{field_name: value})
    def get_adherent_pc(self, queryset, field_name, value):
        return queryset.filter(adherent_pc=value)


    class Meta:
        model = Profil
        fields = {
            'competences': ['icontains', ],
            'description': ['icontains', ],
            "adherent_pc": ['exact', ],
            "adherent_scic": ['exact', ],
            "adherent_rtg": ['exact', ],
            "adherent_citealt": ['exact', ],
        }