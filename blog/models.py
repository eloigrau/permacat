from django.db import models
from bourseLibre.models import Profil
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mass_mail
#from tinymce.models import HTMLField
from django.dispatch import receiver
from django.db.models.signals import post_save

from actstream.models import followers

class Choix():
    statut_projet = ('prop','Proposition de projet'), ("AGO","Fiche prpojet soumise à l'AGO"), ('vote','Soumis au vote'), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_projet = ('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'), ('Projponct','Projet ponctuel'),
    type_annonce = ('Annonce','Annonce'), ('Administratif','Administratif'), ('Agenda','Agenda'), ('Rencontre','Rencontre'), ('Entraide','Entraide'), ('Chantier','Chantier participatif'), ('Jardinage','Jardinage'), ('Recette', 'Recette'), ('Bricolage','Bricolage'), ('Culture','Culture'), ('Bon_plan', 'Bon plan'), ('Point', 'Point de vue'),  ('Autre','Autre'),

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_annonce),
        default='Annonce', verbose_name="categorie")
    titre = models.CharField(max_length=100,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres permacat')
    estModifiable = models.BooleanField(default=False, verbose_name="Modifiable par n'importe qui")

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'article")

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
        return super(Article, self).save(*args, **kwargs)


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
        choices=(Choix.type_projet),
        default='Part', verbose_name="categorie")
    statut = models.CharField(max_length=5,
        choices=(Choix.statut_projet ),
        default='prop', verbose_name="statut")
    titre = models.CharField(max_length=100)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public (cochez) ou Interne (décochez) [réservé aux membres permacat]')
    coresponsable = models.CharField(max_length=150, verbose_name="Référent du projet", default='', null=True, blank=True)
    lien_vote = models.URLField(verbose_name='Lien vers le vote (balotilo.org)', null=True, blank=True, )
    lien_document = models.URLField(verbose_name='Lien vers un document explicatif (en ligne)', default='', null=True, blank=True)
    fichier_projet = models.FileField(upload_to='projets/%Y/%m/', blank=True, default=None, null=True)
    date_fichier = models.DateTimeField(auto_now=True, blank=True)

    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default="", blank=True, null=True)

    estArchive = models.BooleanField(default=False, verbose_name="Archiver le projet")

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()

        return super(Projet, self).save(*args, **kwargs)


@receiver(post_save,  sender=Projet)
def save_projet(instance, **kwargs):
    titre = "Permacat - Articles"
    message = "<a href='www.perma.cat/" + instance.get_absolute_url + "'>L'article '" +  instance.titre + "' a été modifié</a>"+\
              "\n vous recevez cet email, car vous avez choisi de suivre cet article sur le site Permacat"
    emails = [suiv.email for suiv in followers(instance)]
    send_mass_mail([(titre, message, "asso@perma.cat", emails), ])

@receiver(post_save,  sender=Article)
def save_projet(instance, **kwargs):
    titre = "Permacat - Projets"
    message = "<a href='www.perma.cat/" + str(instance.get_absolute_url) + "'>L'article '" +  instance.titre + "' a été modifié</a>"+\
              "\n vous recevez cet email, car vous avez choisi de suivre ce projet sur le site Permacat"
   # emails = [(titre, message, "asso@perma.cat", (suiv.email, )) for suiv in followers(instance)]
    emails = [suiv.email for suiv in followers(instance)]
    send_mass_mail([(titre, message, "asso@perma.cat", emails), ])



class CommentaireProjet(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.projet)
