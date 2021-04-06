from django.db import models
from bourseLibre.models import Profil, Suivis
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager
import uuid

class Choix():
    statut_fiche = ('0','En préparation'), ("1","Intégrée dans le kit"), ('2','En attente' ),
    type_fiche = ('0','Bases de la permaculture'), ('1',"Conception du jardin"), ('2','Réalisation du jardin'), ('3','Récolter'),
    couleurs_fiches = {
        '2':'#4DC490', '1':'#C0EDA0', '3':'#00AA8B', '0':'#FCE79C',
        # '0':"#e0f7de", '1':"#dcc0de",
        # '5':"#d1ecdc",'3':"#fcf6bd", '4':"#d0f4de", '7':"#fff2a0",
        # '9':"#ffc4c8", '2':"#bccacf", '10':"#87bfae", '11':"#bcb4b4"
    }
    statut_fiche = ('0', 'proposition'), ('1', "en cours d'écriture"), ("2", "achevée mais pas validée"), ("3", "validée")
    type_difficulte = ('0', 'facile'), ('1', "moyen"), ("2", "difficile")
    type_jauge = ('1', "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")
    type_budget = ('0', "0"), ('1', "1"), ("2", "2"), ("3", "3")
    type_temps = ('1', "1h"), ("2", "2h"), ("3", "3h"), ("4", "4h"), ("5", "6h"), ("6", "1 journée"),  ("7", "plusieurs jours"),  ("8", "plusieurs mois"),
    type_age = ('0', '3-6 ans'), ('1', "7-11 ans"), ("2", "12 ans et plus"), ("3", "3-11ans"), ("4", "Tout public")
    type_atelier = ('0', 'Observation'), ('1', "Experience"), ("2", "Jardinage")

    def get_categorie(num):
        return Choix.type_fiche[int(num)][1]

    def get_difficulte(num):
        return Choix.type_difficulte[int(num)][1]

    def get_age(num):
        return Choix.type_fiche[int(num)][1]

    def get_typeAtelier(num):
        return Choix.type_atelier[int(num)][1]

    def get_couleur_cat(cat):
            return Choix.couleurs_fiches[cat]

class Fiche(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_fiche),
        default='0', verbose_name="categorie")
    statut = models.CharField(max_length=30,
        choices=(Choix.statut_fiche),
        default='proposition', verbose_name="statut de la fiche")
    numero = models.PositiveIntegerField(blank=False, default=1)
    titre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100, default=uuid.uuid4)
    contenu = models.TextField(null=True, blank=True)
    objectif = models.TextField(null=True, blank=True)
    en_savoir_plus = models.TextField(null=True, blank=True,)


    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, blank=True, null=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)

    tags = TaggableManager(verbose_name=("Mots-clés"), help_text=("Une liste de mots clés, séparés par des virgules."), blank=True,)

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
            return Choix.couleurs_fiches[self.categorie]

    @property
    def get_couleur_cat(self,cat):
            return Choix.couleurs_fiches[cat]


class Atelier(models.Model):
    categorie = models.CharField(max_length=30,
                                 choices=(Choix.type_atelier),
                                 default='0', verbose_name="categorie")
    titre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, default=uuid.uuid4)
    contenu = models.TextField(null=True)
    age = models.CharField(max_length=30,
                                 choices=(Choix.type_age),
                                 default='0', verbose_name="age")
    difficulte = models.CharField(max_length=30,
                                 choices=(Choix.type_difficulte),
                                 default='0', verbose_name="difficulté")
    budget = models.CharField(max_length=30,
                                 choices=(Choix.type_budget),
                                 default='0', verbose_name="budget")
    temps = models.CharField(max_length=30,
                                 choices=(Choix.type_temps),
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
    #
    # @property
    # def get_difficulte(self):
    #     return Choix.type_difficulte[int(self.difficulte)][1]

    # @property
    # def get_budget_html(self):
    #     return "{% fontawesome_icon 'euro-sign' %}"
    #     return "{% fontawesome_icon 'euro-sign' %} ".join([" " for i in range(int(self.budget))])

    @property
    def get_budget_length(self):
        return range(int(self.budget))

    @property
    def get_budget(self):
        return int(self.budget)

    @property
    def get_temps_length(self):
        return range(int(self.temps))

class CommentaireFiche(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    fiche = models.ForeignKey(Fiche, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.fiche)

    def get_absolute_url(self):
        return self.commentaire.get_absolute_url()
