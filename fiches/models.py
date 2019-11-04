from django.db import models
from bourseLibre.models import Profil, Suivis
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mass_mail
#from tinymce.models import HTMLField
from django.dispatch import receiver
from django.db.models.signals import post_save

from actstream.models import followers

class Choix():
    statut_fiche = ('0','En préparation'), ("1","Intégrée dans le kit"), ('2','En attente' ),
    type_fiche = ('0','Bases de la permaculture'), ('1',"conception"), ('2','Réalisation'), ('3','Récolte'),
    couleurs_fiches = {
        '0':"#e0f7de", '1':"#dcc0de", '2':"#d4d1de", '3':"#cebacf",
        '4':"#d1ecdc",'5':"#fcf6bd", '6':"#d0f4de", '7':"#fff2a0",
        '8':"#ffc4c8", '9':"#bccacf", '10':"#87bfae", '11':"#bcb4b4"
    }
    statut_fiche = ('0', 'proposition'), ('1', "en cours d'écriture"), ("2", "achevée mais pas validée"), ("3", "validée")
    type_difficulte = ('0', 'facile'), ('1', "moyen"), ("2", "difficile")
    type_jauge = ('1', "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")
    type_age = ('0', '3-6 ans'), ('1', "7-11 ans"), ("2", "12 ans et plus")
    type_atelier = ('0', 'Observation'), ('1', "Experience"), ("2", "Jardinage")


class Fiche(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_fiche),
        default='0', verbose_name="categorie")
    statut = models.CharField(max_length=30,
        choices=(Choix.statut_fiche),
        default='proposition', verbose_name="statut de la fiche")
    titre = models.CharField(max_length=100,)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    en_savoir_plus = models.TextField(null=True)

    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('fiches:lireFiche', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
        return super(Fiche, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_fiches[self.categorie]
        except:
            return Choix.couleurs_fiches["11"]


class Atelier(models.Model):
    categorie = models.CharField(max_length=30,
                                 choices=(Choix.type_atelier),
                                 default='0', verbose_name="categorie")
    titre = models.CharField(max_length=100, )
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    age = models.CharField(max_length=30,
                                 choices=(Choix.type_age),
                                 default='0', verbose_name="age")
    difficulte = models.CharField(max_length=30,
                                 choices=(Choix.type_difficulte),
                                 default='0', verbose_name="difficulté")
    budget = models.CharField(max_length=30,
                                 choices=(Choix.type_jauge),
                                 default='0', verbose_name="budget")
    temps = models.CharField(max_length=30,
                                 choices=(Choix.type_jauge),
                                 default='0', verbose_name="temps")
    fiche = models.ForeignKey(Fiche, on_delete=models.CASCADE,)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)

    class Meta:
        ordering = ('-date_creation',)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('fiches:lireFiche', kwargs={'slug': self.slug})

    def save(self, commit=False, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
        return super(Atelier, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_fiches[self.categorie]
        except:
            return Choix.couleurs_fiches["11"]


class CommentaireFiche(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    fiche = models.ForeignKey(Fiche, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.fiche)


# @receiver(post_save,  sender=Article)
# def on_save_article(instance, **kwargs):
#     titre = "Permacat - Article actualisé"
#     message = "L'article '" +  instance.titre + "' a été modifié (ou quelqu'un l'a commenté)" +\
#               "\n Vous pouvez y accéder en suivant ce lien : http://www.perma.cat" + instance.get_absolute_url() + \
#               "\n\n------------------------------------------------------------------------------" \
#               "\n vous recevez cet email, car vous avez choisi de suivre ce projet sur le site http://www.Perma.Cat/forum/articles/"
#    # emails = [(titre, message, "asso@perma.cat", (suiv.email, )) for suiv in followers(instance)]
#     emails = [suiv.email for suiv in followers(instance)  if instance.auteur != suiv]
#     try:
#         send_mass_mail([(titre, message, "asso@perma.cat", emails), ])
#     except:
#         pass
