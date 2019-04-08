from django.db import models
from bourseLibre.models import Profil
from django.urls import reverse
#from django.conf import settings
from tinymce.models import HTMLField
import datetime

    
class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(('Annonce','Annonce'), ('Agenda','Agenda'), ('Rencontre','Rencontre'), ('Chantier','Chantier participatif'), ('Jardinage','Jardinage'), ('Recette', 'Recette'), ('Histoire', 'Histoire'), ('Bricolage','Bricolage'), ('Culture','Culture'), ('Bon_plan', 'Bon plan'), ('Point', 'Point de vue'),  ('Autre','Autre'),),
        default='Annonce', verbose_name="categorie")
    titre = models.CharField(max_length=100)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = HTMLField(null=True)
    date = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Date de parution")
    estPublic = models.BooleanField(default=False, verbose_name='Public (cochez) ou Interne (décochez) [réservé aux membres permacat]')

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)

    class Meta:
        ordering = ('date', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)


class Projet(models.Model):
    categorie = models.CharField(max_length=10,
        choices=(('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'),),
        default='Part', verbose_name="categorie")
    statut = models.CharField(max_length=5,
        choices=(('prop','Proposition'), ("AGO","Soumis à l'AGO"), ('vote','Soumis au vote'), ('accep','Accepté'), ('refus','Refusé'), ),
        default='prop', verbose_name="statut")
    titre = models.CharField(max_length=100)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = HTMLField(null=True)
    date = models.DateTimeField(auto_now=True, verbose_name="Date de Modification")
    estPublic = models.BooleanField(default=False, verbose_name='Public (cochez) ou Interne (décochez) [réservé aux membres permacat]')
    coresponsable = models.CharField(max_length=150, default='', null=True, blank=True)
    date_modification = models.DateTimeField(verbose_name="Date de dernière modification", auto_now=True)
    lien_vote = models.URLField(verbose_name='Lien vers le vote (balotilo.org)', null=True, blank=True, )
    lien_document = models.URLField(verbose_name='Lien vers un document explicatif (en ligne)', default='', null=True, blank=True)
    fichier_projet = models.FileField(upload_to='projets/%Y/%m/', blank=True, default=None, null=True)
    date_fichier = models.DateTimeField(auto_now=True, blank=True)

    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default="", blank=True, null=True)

    class Meta:
        ordering = ('date', )

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.slug})

class CommentaireProjet(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.projet)
