# -*- coding: utf-8 -*-
from django.db import models
from django.utils.timezone import now
from django.urls import reverse
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db.models import Q


DEGTORAD=3.141592654/180

LATITUDE_DEFAUT = '42.6976'
LONGITUDE_DEFAUT = '2.8954'

class Choix():
    type_message = ('0','Commentaire'), ("1","Coquille"), ('2','Réflexion')
    type_article = ('0','intro'), ("1","constat"), ('2','preconisations'), ('3','charte'), ('4','liens'), ('5','accueil')
    type_benevole = ('0','Accueil'), ("1","Bar"), ('2','Internet'), ('3','Logistique'), ('4','Concert'), ('5', 'Sécurité'), ('6',"N'importe...")
    type_exposant = ('0','Association'), ("1","Particulier"), ('2','Institution'), ('3','Commerçant'), ('4','Nourriture sur place'), ('5', 'Entreprise de services'), ('6','Conférence'), ('7', 'Atelier'), ('7', "autre")
    type_domaine_exposant = ('0','Agriculture'), ("1","Alimentaire"), ('2','Artisanat'), ('3','Bien être'), ('4','Habitat'), ('5','Informations'), ('6', 'Jeux'), ('7', "autre")

    statut_adhesion = (('', '-----------'),
                     (0, ("Je ne suis pas (ou plus) membre de l'asso 'Ramene Ta Graine'")),
                     (1, ("Je suis déjà adhérent de l'asso 'Ramene Ta graine', ma cotisation est à jour")),
                    (2, ("Je suis déjà adhérent et 'membre équipe' de l'asso 'Ramene Ta graine'"))
                       )
    statut_exposant = (('0', 'Inscription déposée'), ('1', 'Inscription incomplète ou en cours de validation'), ('2', 'Inscription validée'), ('3', 'Inscription refusée'), ('4', 'Inscription annulée'),)
    statut_benevole = (('0', 'Inscription déposée'), ('1', 'Inscription en cours de validation'), ('2', 'Inscription validée'), ('3', 'Inscription refusée'), ('4', 'Inscription annulée'),)



class Profil_agora(AbstractUser):
    description = models.TextField(null=True, blank=True)
    code_postal = models.CharField(max_length=5, blank=True, null=True, default="66000")
    commune = models.CharField(max_length=50, blank=True, null=True, default="Perpignan")
    phone_regex = RegexValidator(regex=r'^\d{9,10}$', message="Le numero de telephone doit contenir 10 chiffres")
    telephone = models.CharField(validators=[phone_regex,], max_length=10, blank=True)  # validators should be a list
    date_registration = models.DateTimeField(verbose_name="Date de création", editable=False)
    inscrit_newsletter = models.BooleanField(verbose_name="J'accepte de recevoir des emails", default=False)
    accepter_conditions = models.BooleanField(verbose_name="J'ai lu et j'accepte les conditions d'utilisation du site", default=False, null=False)
    is_equipe = models.BooleanField(verbose_name="Membre equipe", default=False)
    statut_adhesion = models.IntegerField(choices=Choix.statut_adhesion, default="0")

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_registration = now()
        return super(Profil_agora, self).save(*args, **kwargs)

    def get_nom_class(self):
        return "Profil_agora"

    def get_absolute_url(self):
        return reverse('Profil_agora', kwargs={'user_id':self.id})

    @property
    def inscrit_newsletter_str(self):
       return "oui" if self.inscrit_newsletter else "non"

    @property
    def is_benevole(self):
        benevole = InscriptionBenevole.objects.filter(Q(user=self) & ~Q(statut_benevole=4))
        return len(benevole)>0

    @property
    def is_exposant(self):
        benevole = InscriptionExposant.objects.filter(Q(user=self) & ~Q(statut_exposant=4))
        return len(benevole)>0

    @property
    def nbstands(self):
        exposant = InscriptionExposant.objects.filter(Q(user=self) & ~Q(statut_exposant=4))
        return len(exposant)

    @property
    def is_rtg(self):
        if self.statut_adhesion == 2:
            return True
        else:
            return False
class Message(models.Model):
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil_agora, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    valide = models.BooleanField(verbose_name="validé", default=False)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.auteur) + " " + str(self.date_creation)


    @property
    def get_edit_url(self):
        return reverse('modifierMessage',  kwargs={'id':self.id})

class InscriptionBenevole(models.Model):
    user = models.ForeignKey(Profil_agora, on_delete=models.CASCADE)
    domaine_benevole = models.CharField(max_length=10,
        choices=(Choix.type_benevole),
        default='0', verbose_name="Domaine préférentiel du bénévolat")

    dispo_avantfestival = models.TextField(null=False, blank=True, verbose_name="Quelle est votre disponibilité pour venir aider à la mise en place du festival (les jours précédant le festival) ?")
    description = models.TextField(null=False, blank=True, verbose_name="Remarques, suggestions, infos complémentaires :")
    date_inscription = models.DateTimeField(verbose_name="Date d'inscription", editable=False, auto_now_add=True)


    statut_benevole = models.CharField(max_length=10,
        choices=(Choix.statut_benevole),
        default='0', verbose_name="Statut")

    jour_mer = models.BooleanField(verbose_name="Disponible le Mercredi 27 mai", default=False)
    jour_jeu = models.BooleanField(verbose_name="Disponible le Jeudi 28 mai", default=False)
    jour_ven = models.BooleanField(verbose_name="Disponible le Vendredi 29 mai", default=False)
    jour_sam = models.BooleanField(verbose_name="Disponible le Samedi 30 mai", default=False)
    jour_dim = models.BooleanField(verbose_name="Disponible le Dimanche 31 mai", default=False)
    jour_lun = models.BooleanField(verbose_name="Disponible le Lundi 01 juin", default=False)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.user) + " " + str(self.date_inscription) + " " + str(self.domaine_benevole) + " " + str(self.description)

    @property
    def get_update_url(self):
        return reverse('inscription_benevole_modifier', kwargs={'id':self.id})

    @property
    def get_cancel_url(self):
        return reverse('inscription_benevole_annuler', kwargs={'id':self.id})

    @property
    def get_undocancel_url(self):
        return reverse('inscription_benevole_desannuler', kwargs={'id':self.id})

    @property
    def get_absolute_url(self):
        return reverse('profil', kwargs={'user_id':self.user.id})
    
class InscriptionExposant(models.Model):
    user = models.ForeignKey(Profil_agora, on_delete=models.CASCADE)
    nom_structure = models.TextField(null=False, blank=True, verbose_name="Nom de la structure, association, autre")

    phone_regex = RegexValidator(regex=r'^\d{9,10}$', message="Le numéro de téléphone doit contenir 10 chiffres")
    telephone = models.CharField(verbose_name="Numéro de téléphone de la personne joignable pendant le festival",validators=[phone_regex,], max_length=10, blank=True)  # validators should be a list

    plaque = models.CharField(verbose_name="Numéro de la plaque minéralogique du véhicule utilisé pour le transport du matériel", max_length=10, blank=True)  # validators should be a list

    type_exposant = models.CharField(max_length=10,
        choices=(Choix.type_exposant),
        default='0', verbose_name="Type de la structure")
    domaine_exposant = models.CharField(max_length=10,
        choices=(Choix.type_domaine_exposant),
        default='0', verbose_name="Domaine principal")
    description = models.TextField(null=False, blank=True, verbose_name="Description (brève) du stand que vous voulez tenir")
    nombre_tables =models.CharField(max_length=10,
        choices=((0, '----------'), ('1', 'pas de table'), ('2', "1 table"), ('3', "2 tables")),
        default='0', verbose_name="Combien de tables voulez vous réserver ?")
    is_tombola = models.BooleanField(verbose_name="Je souhaite offrir un lot pour la tombola", default=False)
    lot_tombola = models.TextField(null=True, blank=True, verbose_name="Si oui, quel(s) lot(s) proposez vous pour la tombola?")

    date_inscription = models.DateTimeField(verbose_name="Date d'inscrition", editable=False, auto_now_add=True)
    jours_festival = models.CharField(max_length=10,
                                      choices=(('0', '----------'), ('1', 'Samedi'), ('2', "Dimanche"),
                                               ('3', "Samedi et dimanche"),),
                                      default='0', verbose_name="Quel(s) jour(s) du festival seriez-vous présent ?")

    statut_exposant = models.CharField(max_length=10,
        choices=(Choix.statut_exposant),
        default='0', verbose_name="Statut")

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.user) + " " + str(self.date_inscription) + " " + str(self.domaine_exposant) + " " + str(self.description)

    @property
    def get_update_url(self):
        return reverse('inscription_exposant_modifier', kwargs={'id':self.id})

    @property
    def get_cancel_url(self):
        return reverse('inscription_exposant_annuler', kwargs={'id':self.id})

    @property
    def get_undocancel_url(self):
        return reverse('inscription_exposant_desannuler', kwargs={'id':self.id})

    @property
    def get_absolute_url(self):
        return reverse('profil', kwargs={'user_id':self.user.id})

class InscriptionNewsletter(models.Model):
    email = models.EmailField()
    date_inscription = models.DateTimeField(verbose_name="Date d'inscription", editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return str(self.email)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_inscription = now()
        return super(InscriptionNewsletter, self).save(*args, **kwargs)
