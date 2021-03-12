from bourseLibre.views import getNbNewNotifications
from blog.models import Projet
from ateliers.models import Atelier
from django.utils.timezone import now
from django.db.models import Q

def navbar(request):
    context_data = dict()
    context_data['notification_count'] = getNbNewNotifications(request)

    if request.user.is_authenticated:

        qs_projets = Projet.objects.filter(estArchive=False)
        qs_ateliers = Atelier.objects.filter(date_atelier__gte=now())
        if request.user.adherent_permacat:
            qs_ateliers = qs_ateliers.exclude(asso__abreviation="pc")
            qs_projets = qs_projets.exclude(asso__abreviation="pc")
        if request.user.adherent_rtg:
            qs_ateliers = qs_ateliers.exclude(asso__abreviation="rtg")
            qs_projets = qs_projets.exclude(asso__abreviation="rtg")
        if request.user.adherent_fer:
            qs_ateliers = qs_ateliers.exclude(asso__abreviation="fer")
            qs_projets = qs_projets.exclude(asso__abreviation="fer")
        context_data['liste_projets'] = qs_projets
        context_data['liste_ateliers'] = qs_ateliers

    return context_data