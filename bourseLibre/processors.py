from bourseLibre.views import getNbNewNotifications
from bourseLibre.constantes import Choix as Choix_global
from blog.models import Projet
from ateliers.models import Atelier
from django.utils.timezone import now
from django.utils.functional import SimpleLazyObject

def navbar(request):
    def complicated_query():
        context_data = dict()
        context_data['notification_count'] = getNbNewNotifications(request)

        if request.user.is_authenticated:
            qs_projets = Projet.objects.filter(estArchive=False, statut='accep').order_by('categorie','titre')
            qs_projets_prop = Projet.objects.filter(estArchive=False, statut='prop').order_by('categorie','titre')
            qs_ateliers = Atelier.objects.filter(start_time__gte=now(), estArchive=False).order_by('start_time')

            for nomAsso in Choix_global.abreviationsAsso:
                if not getattr(request.user, "adherent_" + nomAsso):
                    qs_ateliers = qs_ateliers.exclude(asso__abreviation=nomAsso)
                    qs_projets = qs_projets.exclude(asso__abreviation=nomAsso)
                    qs_projets_prop = qs_projets_prop.exclude(asso__abreviation=nomAsso)

            context_data['liste_projets'] = qs_projets
            context_data['liste_projets_prop'] = qs_projets_prop
            context_data['liste_ateliers'] = qs_ateliers

        return context_data

    return SimpleLazyObject(complicated_query)
