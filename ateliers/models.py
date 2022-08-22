from django.db import models
from blog.models import Article
from django.urls import reverse
from django.utils import timezone
import uuid
import datetime as dt
from bourseLibre.models import Profil, Suivis, Asso
from actstream.models import followers
from actstream import action


class Choix():
    type_atelier = ('0','Permaculture'), ('1',"Bricolage"), ('2','Cuisine'), ('3','Bien-être'), ('4',"Musique"), ('6', 'Politique'), ('5', 'Autre...'), ('7', 'Activité Pro'),
    couleurs_ateliers = {
        '2':'#4DC490', '1':'#C0EDA0', '3':'#00AA8B', '0':'#FCE79C',
        # '0':"#e0f7de", '1':"#dcc0de",
        '5':"#d1ecdc",'3':"#fcf6bd", '4':"#d0f4de", '6':"#fff2a0",
        # '9':"#ffc4c8", '2':"#bccacf", '10':"#87bfae", '11':"#bcb4b4"
    }
    statut_atelier = ('0', 'proposition'), ('1', "accepté, en cours d'organisation"), ('2', "accepté, s'est déroule correctement"), ('3', "a été annulé"),
    type_difficulte = ('0', 'facile'), ('1', "moyen"), ("2", "difficile")
    type_jauge = ('1', "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")
    type_budget = ('0', "0"), ('1', "1"), ("2", "2"), ("3", "3")
    type_temps = ('1', "1h"), ("2", "2h"), ("3", "3h"), ("4", "4h"), ("5", "6h"), ("6", "1 journée"),  ("7", "plusieurs jours"),  ("8", "plusieurs mois"),
    type_age = ('0', '3-6 ans'), ('1', "7-11 ans"), ("2", "12 ans et plus"), ("3", "3-11ans"), ("4", "Tout public")
    #type_atelier = ('0', 'Observation'), ('1', "Experience"), ("2", "Jardinage")

    def get_categorie(num):
        return Choix.type_atelier[int(num)][1]

    def get_difficulte(num):
        return Choix.type_difficulte[int(num)][1]

    def get_age(num):
        return Choix.type_atelier[int(num)][1]

    def get_typeAtelier(num):
        return Choix.type_atelier[int(num)][1]

    def get_couleur_cat(cat):
            return Choix.couleurs_ateliers[cat]

class Atelier(models.Model):
    categorie = models.CharField(max_length=30,
        choices=(Choix.type_atelier),
        default='0', verbose_name="categorie")
    statut = models.CharField(max_length=30,
        choices=(Choix.statut_atelier),
        default='proposition', verbose_name="Statut de l'atelier")
    titre = models.CharField(verbose_name="Titre de l'atelier",max_length=120)
    slug = models.SlugField(max_length=100, default=uuid.uuid4)
    description = models.TextField(null=True, blank=True)
    materiel = models.TextField(null=True, blank=True, verbose_name="Matériel/outils nécessaires")
    referent = models.CharField(max_length=120, null=True, blank=True,  verbose_name="Référent(e.s)")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
#    projet = models.OneToOneField(Projet)
    start_time = models.DateField(verbose_name="Date prévue (affichage dans l'agenda)", help_text="(jj/mm/an)", default=timezone.now, blank=True, null=True)
    heure_atelier = models.TimeField(verbose_name="Heure de début", help_text="Horaire de départ (hh:mm)", default="17:00", blank=True, null=True)
    heure_atelier_fin = models.TimeField(verbose_name="Heure de fin ", help_text="Horaire de fin (hh:mm)",
                                    default="19:00", blank=True, null=True)

    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, blank=True, null=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True, help_text="Heure prévue (hh:mm)")
    tarif_par_personne = models.CharField(max_length=100, default='gratuit', help_text="Tarif de l'atelier par personne", verbose_name="Tarif de l'atelier par personne", )
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)

    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'atelier")

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('ateliers:lireAtelier', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()

            try:
                self.auteur
            except:
                self.auteur = Profil.objects.first()

            suivi, created = Suivis.objects.get_or_create(nom_suivi='ateliers')
            emails = [suiv.email for suiv in followers(suivi) if  self.est_autorise(suiv)]

            titre = "Nouvel atelier proposé"
            message = "L'atelier ["+ self.asso.nom +"]' <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' a été proposé"

        ret = super(Atelier, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return ret


    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_ateliers[self.categorie]
        except:
            return Choix.couleurs_ateliers['0']

    @property
    def get_couleur_cat(self, cat):
        try:
            return Choix.couleurs_ateliers[cat]
        except:
            return Choix.couleurs_ateliers['0']


    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True

        return getattr(user, "adherent_" + self.asso.abreviation)


    @property
    def heure_fin_atelier(self,):
        if self.start_time and self.heure_atelier_fin:
            return self.heure_atelier_fin
        else:
            return None

class CommentaireAtelier(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    atelier = models.ForeignKey(Atelier, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.atelier)

    @property
    def get_edit_url(self):
        return reverse('ateliers:modifierCommentaireAtelier',  kwargs={'id':self.id})


    def get_absolute_url(self):
        return self.atelier.get_absolute_url()

class InscriptionAtelier(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    atelier = models.ForeignKey(Atelier, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(verbose_name="Date d'inscritpion", editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.user) + " " + str(self.date_inscription) + " " + str(self.atelier)
