from django.db import models
from bourseLibre.models import Profil, Adresse
from blog.models import Article
import simplejson
from django.urls import reverse
from django.utils import timezone
import uuid
from bourseLibre.models import Profil, Suivis, Asso
import math
from bourseLibre.constantes import DEGTORAD
import requests
from blog.models import Choix as Choix_global
import itertools

# Create your models here.
class Choix:
    statut_projet = ('prop','Proposition de projet'), ("AGO","Projet soumise à l'AGO"), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_reunion_asso = {
        "rtg": ["Réunion équipe", 'Troc de Graine', 'Atelier', 'Rencontre', 'Réunion FestiGraines', 'Autre'],
        "scic": ['Cercle Ancrage', 'Cercle thématique', 'Cercle Education', 'Cercle Jardins', 'Evenement', 'Divers',]
      }

    type_reunion = [(str(i), y) for i, y in enumerate([x for x in list(itertools.chain.from_iterable(type_reunion_asso.values()))])]

    ordre_tri_reunions = {
                        "Date <":'-start_time',
                        "Date >":'start_time',
                        "Titre":'titre',
                        "Catégorie":'categorie',
    }

def get_typereunion(asso):
    return [(str(i), y) for i, y in enumerate([x for x in Choix.type_reunion_asso[asso]])]


class ParticipantReunion(models.Model):
    nom = models.CharField(verbose_name="Nom du participant", max_length=120)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE,)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    #vehicule = models.BooleanField(default=True, verbose_name="Est venu.e avec son véhicule")

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('defraiement:lireParticipant', kwargs={'id': self.id})

    def get_adresse_str(self):
        return self.adresse.get_adresse_str

    def getLatLon(self):
        return self.adresse.getLatLon()

    def getDistance(self, reunion):
        try:
            x1 = float(self.adresse.latitude)*DEGTORAD
            y1 = float(self.adresse.longitude)*DEGTORAD
            x2 = float(reunion.adresse.latitude)*DEGTORAD
            y2 = float(reunion.adresse.longitude)*DEGTORAD
            x = (y2-y1) * math.cos((x1+x2)/2)
            y = (x2-x1)

            return math.sqrt(x*x + y*y) * 6371
        except:
            return 0

    def get_url(self, reunion):
        latlon_1 = str(self.adresse.longitude).replace(',', '.') + "," + str(self.adresse.latitude).replace(',', '.')
        latlon_2 = str(reunion.adresse.longitude).replace(',', '.') + "," + str(reunion.adresse.latitude).replace(',',
                                                                                                                  '.')
        url = "http://router.project-osrm.org/route/v1/driving/" + latlon_1 + ";" + latlon_2 + "?overview=false"

        return url

    def get_gmaps_url(self, reunion):
        latlon_1 = str(self.adresse.latitude).replace(',', '.') + "," + str(self.adresse.longitude).replace(',', '.')
        latlon_2 = str(reunion.adresse.latitude).replace(',', '.') + "," + str(reunion.adresse.longitude).replace(',','.')
        url = "https://www.google.com/maps/dir/'" + latlon_1 + "'/'" + latlon_2 +"'"

        return url

    def getDistance_route(self, reunion, recalculer=False):
        distanceObject, created = Distance_ParticipantReunion.objects.get_or_create(reunion=reunion, participant=self)
        if not recalculer:
            return float(distanceObject.getDistance())
        else:
            return float(distanceObject.calculerDistance())


    def getDistance_routeTotale(self):
        dist = 0
        for r in self.reunion_set.all():
            dist += float(self.getDistance_route(r))
        return round(dist, 1)


class Reunion(models.Model):
    categorie = models.CharField(max_length=30,
                                 choices=(Choix.type_reunion),
                                 default='0', verbose_name="categorie")
    titre = models.CharField(verbose_name="Titre de la rencontre", max_length=120)
    slug = models.SlugField(max_length=100, default=uuid.uuid4)
    description = models.TextField(null=True, blank=True)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    start_time = models.DateField(verbose_name="Date de la rencontre", help_text="(jj/mm/an)",
                                  default=timezone.now, blank=True, null=True)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, null=True, blank=True,)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver la réunion")
    participants = models.ManyToManyField(ParticipantReunion,
                                help_text="Le participant doit etre associé à une reunion existante (sinon créez d'abord la reunion)")

    class Meta:
        ordering = ('-date_creation',)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('defraiement:lireReunion', kwargs={'slug': self.slug})


    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True

        return getattr(user, "adherent_" + self.asso.abreviation)

    @property
    def getDistanceTotale(self):
        dist = 0
        for p in self.participants.all():
            try:
                dist += p.getDistance_route(self)
            except:
                return -1
        return round(dist, 2)

    def recalculerDistance(self):
        for p in self.participants.all():
            p.getDistance_route(self, recalculer=True)

    @property
    def get_logo_nomgroupe(self):
        return Choix_global.get_logo_nomgroupe(self.asso.abreviation)

    @property
    def get_logo_nomgroupe_html(self):
        return self.get_logo_nomgroupe_html_taille(20)

    def get_logo_nomgroupe_html_taille(self, taille=20):
        return "<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

class Distance_ParticipantReunion(models.Model):
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE, null=True, blank=True, )
    participant = models.ForeignKey(ParticipantReunion, on_delete=models.CASCADE, null=True, blank=True, )
    distance = models.TextField(blank=True, null=True, verbose_name="Distance calculée")
    contexte_distance = models.TextField(blank=True, null=True, verbose_name="Description du contexte")

    class Meta:
        unique_together = (('reunion', 'participant',), )

    def save(self, calculerDistance=False, *args, **kwargs):
        ''' On save, update timestamps '''
        retour = super(Distance_ParticipantReunion, self).save(*args, **kwargs)
        if calculerDistance or not self.distance:
            self.distance = self.calculerDistance()
        return retour

    def getDistance(self):
        if self.distance:
            return self.distance
        else:
            return self.calculerDistance()

    def calculerDistance(self):
        try:
            reponse = requests.get(self.participant.get_url(self.reunion))
            data = simplejson.loads(reponse.text)
            if data["code"] != "Ok":
                raise Exception("erreur de calcul de trajet")
            routes = data["routes"]
            self.contexte_distance = str(routes)
            dist = 100000000
            for r in routes[0]:
                if routes[0]["distance"] < dist:
                    dist = float(routes[0]["distance"])
            if dist == 100000000:
                dist = -1
        except:
            dist = -1
        self.distance = str(round(dist/1000.0, 2))
        self.save(calculerDistance=False)
        return self.distance


# class Atelier(models.Model):
#     categorie = models.CharField(max_length=30,
#                                  choices=(Choix.type_atelier),
#                                  default='0', verbose_name="categorie")
#     statut = models.CharField(max_length=30,
#                               choices=(Choix.statut_atelier),
#                               default='proposition', verbose_name="Statut de l'atelier")
#     titre = models.CharField(verbose_name="Titre de l'atelier", max_length=120)
#     slug = models.SlugField(max_length=100, default=uuid.uuid4)
#     description = models.TextField(null=True, blank=True)
#     materiel = models.TextField(null=True, blank=True, verbose_name="Matériel/outils nécessaires")
#     referent = models.CharField(max_length=120, null=True, blank=True, verbose_name="Référent(e.s)")
#     auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
#     #    projet = models.OneToOneField(Projet)
#     start_time = models.DateField(verbose_name="Date prévue (affichage dans l'agenda)", help_text="(jj/mm/an)",
#                                   default=timezone.now, blank=True, null=True)
#     heure_atelier = models.TimeField(verbose_name="Heure prévue", help_text="Horaire de départ (hh:mm)",
#                                      default="17:00", blank=True, null=True)
#
#     date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
#     date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
#
#     date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, blank=True,
#                                                null=True)
#     dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True,
#                                       help_text="Heure prévue (hh:mm)")
#     duree_prevue = models.TimeField(verbose_name="Durée prévue", help_text="Durée de l'atelier estimée",
#                                     default="02:00", blank=True, null=True)
#     tarif_par_personne = models.CharField(max_length=100, default='gratuit',
#                                           help_text="Tarif de l'atelier par personne",
#                                           verbose_name="Tarif de l'atelier par personne", )
#     asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
#
#     estArchive = models.BooleanField(default=False, verbose_name="Archiver l'atelier")
#
#     class Meta:
#         ordering = ('-date_creation',)
#
#     def __str__(self):
#         return self.titre
#
#     def get_absolute_url(self):
#         return reverse('ateliers:lireAtelier', kwargs={'slug': self.slug})
