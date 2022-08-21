from bourseLibre.models import Suivis
from bourseLibre.constantes import Choix


def get_suivis_forum(request):
    return [("Public", 'public', Suivis.objects.get_or_create(nom_suivi="articles_public")[0]), ] + [
        (nom_asso, abreviation, Suivis.objects.get_or_create(nom_suivi="articles_" + abreviation)[0]) for
        abreviation, nom_asso in Choix.abreviationsNomsAsso ]