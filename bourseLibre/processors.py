from bourseLibre.views import getNbNewNotifications
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
            qs_ateliers = Atelier.objects.filter(date_atelier__gte=now()).order_by('categorie')
            if not request.user.adherent_permacat:
                qs_ateliers = qs_ateliers.exclude(asso__abreviation="pc")
                qs_projets = qs_projets.exclude(asso__abreviation="pc")
                qs_projets_prop = qs_projets_prop.exclude(asso__abreviation="pc")
            if not request.user.adherent_rtg:
                qs_ateliers = qs_ateliers.exclude(asso__abreviation="rtg")
                qs_projets = qs_projets.exclude(asso__abreviation="rtg")
                qs_projets_prop = qs_projets_prop.exclude(asso__abreviation="rtg")
            if not request.user.adherent_fer:
                qs_ateliers = qs_ateliers.exclude(asso__abreviation="fer")
                qs_projets = qs_projets.exclude(asso__abreviation="fer")
                qs_projets_prop = qs_projets_prop.exclude(asso__abreviation="fer")
            context_data['liste_projets'] = qs_projets
            context_data['liste_projets_prop'] = qs_projets_prop
            context_data['liste_ateliers'] = qs_ateliers

        return context_data

    return SimpleLazyObject(complicated_query)
