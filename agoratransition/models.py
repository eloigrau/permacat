from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

# Create your models here.
class Choix():
    typeInscription = ('0','Association'), ("1","Particulier"), ('2','Institution'), ('3', 'Entreprise'),  ('4', "autre"),
    statut_exposant = (('0', 'Inscription déposée'), ('1', 'Inscription incomplète ou en cours de validation'), ('5', 'Inscription valide mais en attente du cheque de caution'), ('2', 'Inscription validée'), ('3', 'Inscription refusée'), ('4', 'Inscription annulée'),)

class InscriptionExposant(models.Model):
    user = models.TextField(null=False, blank=True, verbose_name="Nom prénom / Raison sociale")
    nom_structure = models.TextField(null=False, blank=True, verbose_name="Nom de la structure, association, autre")

    phone_regex = RegexValidator(regex=r'^\d{9,10}$', message="Le numéro de téléphone doit contenir 10 chiffres")
    telephone = models.CharField(verbose_name="Numéro de téléphone de la personne joignable pendant le festival",
                                 validators=[phone_regex, ], max_length=10,
                                 blank=True)  # validators should be a list

    type_inscription = models.CharField(max_length=10,
                                     choices=(Choix.typeInscription),
                                     default='0', verbose_name="Type de la structure")
    date_inscription = models.DateTimeField(verbose_name="Date d'inscrition", editable=False, auto_now_add=True)

    statut_exposant = models.CharField(max_length=10,
                                       choices=(Choix.statut_exposant),
                                       default='0', verbose_name="Statut")

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.user) + " " + str(self.date_inscription) + " " + str(
            self.statut_exposant) + " " + str(self.description)
