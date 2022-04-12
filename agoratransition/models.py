from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

# Create your models here.
class Choix():
    type_inscription = ("0","Particulier"), ('1','Association'), ('2','Institution'), ('3', 'Entreprise'),  ('4', "autre"),
    statut_inscription = (('0', 'Inscription déposée'), ('1', 'Inscription incomplète ou en cours de validation'), ('5', 'Inscription valide mais en attente du cheque de caution'), ('2', 'Inscription validée'), ('3', 'Inscription refusée'), ('4', 'Inscription annulée'),)

class InscriptionExposant(models.Model):
    nom = models.CharField(max_length=250, null=False, blank=True, verbose_name="Nom Prénom / Raison sociale*")
    email = models.EmailField(blank=False, max_length=254, verbose_name='Email*',)

    telephone = models.CharField(verbose_name="Numéro de téléphone", max_length=10,
                                 blank=True)  # validators should be a list

    type_inscription = models.CharField(max_length=3,
                                     choices=(Choix.type_inscription),
                                     default='0', verbose_name="Type de structure")
    date_inscription = models.DateTimeField(verbose_name="Date d'inscrition", editable=False, auto_now_add=True)

    statut_exposant = models.CharField(max_length=3,
                                       choices=(Choix.statut_inscription),
                                       default='0', verbose_name="Statut")
    commentaire = models.TextField(null=False, blank=True, verbose_name="Commentaire / message à passer")

    class Meta:
        unique_together = (('nom', 'email',), )

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.nom) + " " + str(self.date_inscription) + " " + str(
            self.statut_exposant) + " " + str(self.commentaire)



class Proposition(models.Model):
    nom = models.CharField(max_length=250, null=False, blank=False, verbose_name="Nom Prénom / Raison sociale*")
    email = models.EmailField(blank=False, max_length=254, verbose_name='Email*',)
    telephone = models.CharField(verbose_name="Numéro de téléphone", max_length=10,
                                 blank=True)  # validatErs should be a list

    proposition = models.TextField(null=False, blank=False, verbose_name="Proposition de question / table ronde*",)

    animeParProposant = models.BooleanField(default=False, null=True, verbose_name="Je suis pret.e à animer une table ronde à ce sujet")

    date_inscription = models.DateTimeField(verbose_name="Date d'inscrition", editable=False, auto_now_add=True)

    class Meta:
        unique_together = (('proposition', 'email',), )


    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.nom) + " " + str(self.date_inscription) + " " + str(
            self.animeParProposant) + " " + str(self.proposition)

class Message_agora(models.Model):
    email = models.EmailField(verbose_name="Email")
    nom = models.CharField(max_length=250, verbose_name="Nom prénom / Raison sociale",)
    msg = models.TextField(verbose_name="Message", )

