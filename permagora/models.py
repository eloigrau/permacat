# -*- coding: utf-8 -*-
from django.db import models
from django.urls import reverse
from bourseLibre.models import Profil
from django.template.defaultfilters import slugify

DEGTORAD=3.141592654/180

LATITUDE_DEFAUT = '42.6976'
LONGITUDE_DEFAUT = '2.8954'

class Choix():
    type_message = ('0','Commentaire'), ("1","Coquille"), ('2','Réflexion')
    type_article = ('0','intro'), ("1","constat"), ('2','preconisations'), ('3','charte'), ('4','liens'), ('5','accueil')


class Message_permagora(models.Model):
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    type_message = models.CharField(max_length=10,
        choices=(Choix.type_message),
        default='0', verbose_name="type de commentaire")
    type_article = models.CharField(max_length=10,
        choices=(Choix.type_article),
        default='0', verbose_name="reaction à")
    valide = models.BooleanField(verbose_name="validé", default=False)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.auteur) + " " + str(self.date_creation)


class Domaine_charte(models.Model):
    titre = models.TextField(null=False, blank=False)
    slug = models.SlugField(max_length=100)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)[:99]
        super(Domaine_charte, self).save(*args, **kwargs)

    def __str__(self):
        return self.titre

class Proposition_charte(models.Model):
    domaine = models.ForeignKey(Domaine_charte, on_delete=models.CASCADE)
    titre = models.TextField(null=False, blank=False)
    resources = models.TextField(null=True, blank=True, verbose_name="Ressources associées (articles, vidéos, ...)")
    contexte = models.TextField(null=True, blank=True, verbose_name="Matériel/outils nécessaires")
    besoins = models.TextField(null=True, blank=True, verbose_name="Besoins pour mettre en place les solutions")
    ideal = models.TextField(null=True, blank=True, verbose_name="Ce qu'il faudrait faire idéalement")
    existant = models.TextField(null=True, blank=True, verbose_name="Existant déjà sur le territoire (association, projet, ...)")
    actions = models.TextField(null=True, blank=True, verbose_name="Actions effectuées ou envisagées")

    compteur_plus = models.IntegerField(default=0)
    compteur_moins = models.IntegerField(default=0)
    slug = models.SlugField(max_length=100)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)[:99]
        super(Proposition_charte, self).save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('permagora:voirPropositionCharte', kwargs={'slug':self.slug})


class Commentaire_charte(models.Model):
    proposition = models.ForeignKey(Proposition_charte, on_delete=models.CASCADE)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    message = models.TextField(null=False, blank=True,)
    date_creation = models.DateTimeField(auto_now_add=True)
    type_message = models.CharField(max_length=10,
        choices=(Choix.type_message),
        default='0', verbose_name="type de commentaire")

    def __str__(self):
        return self.message

class Vote(models.Model):
    proposition = models.ForeignKey(Proposition_charte, on_delete=models.CASCADE)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    type_vote=models.CharField(max_length=10,
        choices=((0, "neutre"), (1, "plus"), (2, "moins"), ),
        default='0', verbose_name="type de commentaire")


    def __str__(self):
        return self.type_vote