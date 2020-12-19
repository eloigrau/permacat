# -*- coding: utf-8 -*-
import decimal
import math
import os
from datetime import date

import django_filters
import requests
from actstream import actions, action
from actstream.models import following, followers
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
# from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager
from stdimage import StdImageField

from .constantes import Choix, DEGTORAD


# from tinymce.models import HTMLField
#from blog.models import Article

def get_categorie_from_subcat(subcat):
    for type_produit, dico in Choix.choix.items():
        if str(subcat) in dico['souscategorie']:
            return type_produit
    return "Catégorie inconnue (souscategorie : " + str(subcat) +")"

LATITUDE_DEFAUT = '42.6976'
LONGITUDE_DEFAUT = '2.8954'
#from django.contrib.gis.db import models as models_gis
class Adresse(models.Model):
    rue = models.CharField(max_length=200, blank=True, null=True)
    code_postal = models.CharField(max_length=5, blank=True, null=True, default="66000")
    commune = models.CharField(max_length=50, blank=True, null=True, default="Perpignan")
    latitude = models.FloatField(blank=True, null=True, default=LATITUDE_DEFAUT)
    longitude = models.FloatField(blank=True, null=True, default=LONGITUDE_DEFAUT)
    pays = models.CharField(max_length=12, blank=True, null=True, default="France")
    phone_regex = RegexValidator(regex=r'^\d{9,10}$', message="Le numero de telephone doit contenir 10 chiffres")
    telephone = models.CharField(validators=[phone_regex,], max_length=10, blank=True)  # validators should be a list


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.set_latlon_from_adresse()
        return super(Adresse, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('profil_courant')

    def __str__(self):
        if self.commune:
            return "("+str(self.id)+") "+self.commune 
        else:
            return "("+str(self.id)+") "+self.code_postal

    def __unicode__(self):
        return self.__str__()

    def set_latlon_from_adresse(self):
        address = ''
        if self.rue:
            address += self.rue + ", "
        address += self.code_postal
        if self.commune:
            address += " " + self.commune
        address += ", " + self.pays
        try:
            api_key = os.environ["GAPI_KEY"]
            api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
            api_response_dict = api_response.json()

            if api_response_dict['status'] == 'OK':
                self.latitude = api_response_dict['results'][0]['geometry']['location']['lat']
                self.longitude = api_response_dict['results'][0]['geometry']['location']['lng']
        except:
            pass

    def get_latitude(self):
        if not self.latitude:
            return LATITUDE_DEFAUT
        return str(self.latitude).replace(",",".")

    def get_longitude(self):
        if not self.longitude:
            return LONGITUDE_DEFAUT
        return str(self.longitude).replace(",",".")


class Asso(models.Model):
    nom = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10)
    email = models.EmailField(null=True)
    date_inscription = models.DateTimeField(verbose_name="Date d'inscription", editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return str(self.nom)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_inscription = now()
        return super(Asso, self).save(*args, **kwargs)

    def is_membre(self, user):
        if self.nom == "permacat" and not user.adherent_permacat:
            return False
        elif self.nom == "rtg" and not user.adherent_rtg:
            return False
        return True

    def getProfils(self):
        if self.abreviation == "public":
            return Profil.objects.filter()
        elif self.abreviation == "pc":
            return Profil.objects.filter(adherent_permacat=True)
        elif self.abreviation == "rtg":
            return Profil.objects.filter(adherent_rtg=True)
        elif self.abreviation == "ame":
            return Profil.objects.filter(adherent_ame=True)
        elif self.abreviation == "ga":
            return Profil.objects.filter(adherent_ga=True)

class Profil(AbstractUser):
    username_validator = ASCIIUsernameValidator()
    site_web = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    competences = models.TextField(null=True, blank=True)
    adresse = models.OneToOneField(Adresse, on_delete=models.CASCADE)
    avatar = StdImageField(null=True, blank=True, upload_to='avatars/', variations={
        'large': (640, 480),
        'thumbnail2': (100, 100, True)})

    date_registration = models.DateTimeField(verbose_name="Date de création", editable=False)
    pseudo_june = models.CharField(_('pseudo Monnaie Libre'), blank=True, default=None, null=True, max_length=50)

    inscrit_newsletter = models.BooleanField(verbose_name="J'accepte de recevoir des emails de Permacat", default=False)
    statut_adhesion = models.IntegerField(choices=Choix.statut_adhesion, default="0")
    #statut_adhesion_rtg = models.IntegerField(choices=Choix.statut_adhesion_rtg, default="0")
    #statut_adhesion_ga = models.IntegerField(choices=Choix.statut_adhesion_ga, default="0")
    cotisation_a_jour = models.BooleanField(verbose_name="Cotisation à jour", default=False)
    adherent_permacat = models.BooleanField(verbose_name="Je suis adhérent de Permacat", default=False)
    adherent_rtg = models.BooleanField(verbose_name="Je suis adhérent de Ramene Ta Graine", default=False)
    adherent_ga = models.BooleanField(verbose_name="Je suis adhérent de Gaïarmonie", default=False)
    accepter_conditions = models.BooleanField(verbose_name="J'ai lu et j'accepte les conditions d'utilisation du site", default=False, null=False)
    accepter_annuaire = models.BooleanField(verbose_name="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous", default=True)
    is_jardinpartage = models.BooleanField(verbose_name="Je suis intéressé.e par les jardins partagés", default=False)

    date_notifications = models.DateTimeField(verbose_name="Date de validation des notifications",default=now)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_registration = now()
        if not hasattr(self, 'adresse') or not self.adresse:
             self.adresse = Adresse.objects.create()

        return super(Profil, self).save(*args, **kwargs)

    def get_nom_class(self):
        return "Profil"

    def get_absolute_url(self):
        return reverse('profil', kwargs={'user_id':self.id})

    def getDistance(self, profil):
        x1 = float(self.adresse.latitude)*DEGTORAD
        y1 = float(self.adresse.longitude)*DEGTORAD
        x2 = float(profil.adresse.latitude)*DEGTORAD
        y2 = float(profil.adresse.longitude)*DEGTORAD
        x = (y2-y1) * math.cos((x1+x2)/2)
        y = (x2-x1)
        return math.sqrt(x*x + y*y) * 6371

    @property
    def statutMembre(self):
        return self.statut_adhesion

    @property
    def statutMembre_asso(self, asso):
        if asso == "permacat":
            return self.adherent_permacat
        elif asso == "rtg":
            return self.adherent_rtg

    @property
    def statutMembre_str(self):
        if self.statut_adhesion == 0:
            return "souhaite devenir membre de l'association"
        elif self.statut_adhesion == 1:
            return "ne souhaite pas devenir membre"
        elif self.statut_adhesion == 2:
            return "membre actif"

    @property
    def statutMembre_str_asso(self, asso):
        if asso == "permacat":
            if self.adherent_permacat:
                return "membre actif de Permacat"
            else:
                return "Non membre de Permacat"
        if asso == "rtg":
            if self.adherent_rtg:
                return "membre actif de 'Ramene Ta Graine'"
            else:
                return "Non membre de 'Ramene Ta Graine'"

    def estMembre_str(self, nom_asso):
        if nom_asso == "Public" or nom_asso == "public":
            return True
        elif (nom_asso == "Permacat" or nom_asso == "pc") and self.adherent_permacat:
            return True
        elif self.adherent_rtg and (nom_asso == "Ramène Ta Graine" or nom_asso == "rtg") :
            return True
        else:
            return False

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True
        elif self.asso.abreviation == "pc":
            return user.adherent_permacat
        elif self.asso.abreviation == "rtg":
            return user.adherent_rtg
        else:
            return False

    @property
    def cotisation_a_jour_str(self):
       return "oui" if self.cotisation_a_jour else "non"

    @property
    def inscrit_newsletter_str(self):
       return "oui" if self.inscrit_newsletter else "non"

@receiver(post_save, sender=Profil)
def create_user_profile(sender, instance, created, **kwargs):
    if created :
        for suiv in ['produits', 'articles', 'projets', 'conversations', 'suffrages']:
            suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)
            actions.follow(instance, suivi, actor_only=True, send_action=False)
        action.send(instance, verb='inscription', url=instance.get_absolute_url(),
                    description="s'est inscrit.e sur le site")
        if instance.is_superuser:
            Panier.objects.create(user=instance)


class Adhesion_permacat(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_cotisation = models.DateField(verbose_name="Date de la cotisation", editable=True, auto_now_add=False)
    montant = models.CharField(max_length=50, blank=True, verbose_name="Montant de l'adhesion")

    def __str__(self):
        return self.user.username + " le "+ str(self.date_cotisation) + " " + str(self.montant)

class Produit(models.Model):  # , BaseProduct):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE,)
    date_creation = models.DateTimeField(verbose_name="Date de parution", editable=False)
    date_debut = models.DateField(verbose_name="Débute le (jj/mm/an)", null=True, blank=True)
    #proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
    date_expiration = models.DateField(verbose_name="Expire le (jj/mm/an)", blank=True, null=True, )#default=proposed_renewal_date, )
    nom_produit = models.CharField(max_length=250, verbose_name="Titre de l'annonce")
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100)

    stock_initial = models.FloatField(default=1, verbose_name="Quantité disponible", max_length=250, validators=[MinValueValidator(1), ])
    stock_courant = models.FloatField(default=1, max_length=250, validators=[MinValueValidator(0), ])
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True, validators=[MinValueValidator(0), ])
    unite_prix = models.CharField(
        max_length=8,
        choices = Choix.monnaies,
        default='lliure', verbose_name="monnaie"
    )

    CHOIX_CATEGORIE = (('aliment', 'aliment'),('vegetal', 'végétal'), ('service', 'service'), ('objet', 'objet'))
    categorie = models.CharField(max_length=20,
                                 choices=CHOIX_CATEGORIE,
                                 default='aliment')
    #photo = models.ImageField(blank=True, upload_to="imagesProduits/")
    #photo = StdImageField(upload_to='imagesProduits/', blank=True, variations={'large': (640, 480), 'thumbnail': (100, 100, True)}) # all previous features in one declaration

    estUneOffre = models.BooleanField(default=True, verbose_name='Offre (cochez) ou Demande (décochez)')
    estPublique = models.BooleanField(default=False, verbose_name='Publique (cochez) ou Interne (décochez) [réservé aux membres permacat]')
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    objects = InheritanceManager()

    @property
    def slug(self):
        return slugify(self.nom_produit)

    @property
    def est_perimee(self):
        if not self.date_expiration:
            return False
        return date.today() > self.date_expiration

    def __str__(self):
        return self.nom_produit

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = now()
            self.stock_courant = self.stock_initial
            suivi, cree = Suivis.objects.get_or_create(nom_suivi='produits')
            titre = "[Permacat] nouveau produit"
            emails = [suiv.email for suiv in followers(suivi) if
                      self.user != suiv and self.est_autorise(suiv)]

        retour = super(Produit, self).save(*args, **kwargs)

        if emails:
            if self.estUneOffre:
                message = "Nouvelle offre au marché : <a href='https://permacat.herokuapp.com" + self.get_absolute_url() +"'>" + self.nom_produit + "</a>"
            else:
                message = "Nouvelle demande au marché : <a href='https://permacat.herokuapp.com" + self.get_absolute_url() +"'>" + self.nom_produit + "</a>"
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour


    def get_absolute_url(self):
        return reverse('produit_detail', kwargs={'produit_id':self.id})

    def get_type_prix(self):
        return Produit.objects.get_subclass(id=self.id).type_prix

    def get_unite_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.unite_prix
        elif self.get_prix() == 0:
            return "gratuit"
        else:
            return Produit.objects.get_subclass(id=self.id).get_unite_prix()
            # return prod.get_unite_prix()

    def get_prixEtUnite(self):
        return Produit.objects.get_subclass(id=self.id).get_prixEtUnite()

    def get_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return 0
        else:
            return round(self.prix, 2)

    def get_nom_class(self):
        return "Produit"

    def get_souscategorie(self):
        return"standard"

    def get_message_demande(self):
        return "[A propos de l'annonce de '" + self.nom_produit + "']: "

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True
        elif self.asso.abreviation == "pc":
            return user.adherent_permacat
        elif self.asso.abreviation == "rtg":
            return user.adherent_rtg
        else:
            return False

    @property
    def est_public(self):
        return self.asso.id == 1


class Produit_aliment(Produit):  # , BaseProduct):
    type = 'aliment'
    couleur = models.CharField(
        max_length=20,
        choices=((Choix.couleurs['aliment'], Choix.couleurs['aliment']),),
        default=Choix.couleurs['aliment']
    )
    souscategorie = models.CharField(
        max_length=20,
        choices=((cat,cat) for cat in Choix.choix[type]['souscategorie']),
        default=Choix.choix[type]['souscategorie'][0][0]
    )
    #etat = models.CharField(
    #    max_length=20,
    #   choices=Choix.choix[type]['etat'],
    #    default=Choix.choix[type]['etat'][0][0]
    #)
    type_prix = models.CharField(
        max_length=20,
        choices=Choix.choix[type]['type_prix'],
        default=Choix.choix[type]['type_prix'][0][0], verbose_name="par"
    )
    def get_unite_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.unite_prix
        else:
            return self.unite_prix + "/" + self.get_type_prix_display()

    def get_prixEtUnite(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.get_unite_prix_display()
        elif self.get_prix() == 0:
            return "gratuit"
        return str(self.get_prix()) + " " + self.get_unite_prix()

    def get_souscategorie(self):
        return "aliment"

class Produit_vegetal(Produit):  # , BaseProduct):
    type = 'vegetal'
    couleur = models.CharField(
        max_length=20,
        choices=((Choix.couleurs['vegetal'], Choix.couleurs['vegetal']),),
        default=Choix.couleurs['vegetal']
    )
    souscategorie = models.CharField(
        max_length=20,
        choices=((cat,cat) for cat in Choix.choix[type]['souscategorie']),
        default=Choix.choix[type]['souscategorie'][0][0]
    )
    #etat = models.CharField(
    #   max_length=20,
    #   choices=Choix.choix[type]['etat'],
    #   default=Choix.choix[type]['etat'][0][0]
    #)
    type_prix = models.CharField(
        max_length=20,
        choices=Choix.choix[type]['type_prix'],
        default=Choix.choix[type]['type_prix'][0][0], verbose_name="par"
    )

    def get_unite_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.unite_prix
        else:
            return self.unite_prix + "/" + self.get_type_prix_display()

    def get_prixEtUnite(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.get_unite_prix_display()
        elif self.get_prix() == 0:
            return "gratuit"
        return str(self.get_prix()) + " " + self.get_unite_prix()

    def get_souscategorie(self):
        return"vegetal"

class Produit_service(Produit):  # , BaseProduct):
    type = 'service'
    couleur = models.CharField(
        max_length=20,
        choices=((Choix.couleurs['service'], Choix.couleurs['service']),),
        default=Choix.couleurs['service']
    )
    souscategorie = models.CharField(
        max_length=20,
        choices=((cat,cat) for cat in Choix.choix[type]['souscategorie']),
        default=Choix.choix["service"]['souscategorie'][0][0]
    )
    #etat = models.CharField(
    #    max_length=20,
    #   choices=Choix.choix["service"]['etat'],
    #   default=Choix.choix["service"]['etat'][0][0]
    #)
    type_prix = models.CharField(
        max_length=20,
        choices=Choix.choix["service"]['type_prix'],
        default=Choix.choix["service"]['type_prix'][0][0], verbose_name="par"
    )

    def get_unite_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.get_unite_prix_display()
        else:
            return self.unite_prix + "/" + self.get_type_prix_display()

    def get_prixEtUnite(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.get_unite_prix_display()
        elif self.get_prix() == 0:
            return "gratuit"
        return str(self.get_prix()) + " " + self.get_unite_prix()

    def get_souscategorie(self):
        return "service"

class Produit_objet(Produit):  # , BaseProduct):
    type = 'objet'
    couleur = models.CharField(
        max_length=20,
        choices=((Choix.couleurs['objet'], Choix.couleurs['objet']),),
        default=Choix.couleurs['objet']
    )
    souscategorie = models.CharField(
        max_length=20,
        choices=((cat,cat) for cat in Choix.choix[type]['souscategorie']),
        default=Choix.choix[type]['souscategorie'][0][0]
    )
    #etat = models.CharField(
    #   max_length=20,
    #    choices=Choix.choix[type]['etat'],
    #   default=Choix.choix[type]['etat'][0][0]
    #)
    type_prix = models.CharField(
        max_length=20,
        choices=Choix.choix[type]['type_prix'],
        default=Choix.choix[type]['type_prix'][0][0], verbose_name="par"
    )

    def get_unite_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.get_unite_prix_display()
        else:
            return self.unite_prix + "/" + self.get_type_prix_display()

    def get_prixEtUnite(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.get_unite_prix_display()
        elif self.get_prix() == 0:
            return "gratuit"
        return str(self.get_prix()) + " " + self.get_unite_prix()

    def get_souscategorie(self):
        return "objet"

class ItemAlreadyExists(Exception):
    pass

class ItemDoesNotExist(Exception):
    pass


class ProductFilter(django_filters.FilterSet):
    #nom_produit = django_filters.CharFilter(lookup_expr='iexact')
    # date_creation = django_filters.DateFromToRangeFilter(name='date_creation',)
    # date_debut = django_filters.DateFromToRangeFilter(name='date_debut')
    # date_expiration = django_filters.DateFromToRangeFilter(name='date_expiration')
    categorie = django_filters.ChoiceFilter(label='categorie', lookup_expr='exact', )
    username = django_filters.ModelChoiceFilter(label='producteur', queryset=Profil.objects.all())
    nom_produit = django_filters.CharFilter(label='titre', lookup_expr='contains')
    description = django_filters.CharFilter(label='description', lookup_expr='contains')
    prixmin = django_filters.NumberFilter(label='prix min', lookup_expr='gt', name="prix")
    prixmax = django_filters.NumberFilter(label='prix max', lookup_expr='lt', name="prix")
    # date_debut = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}), label='date de début')
    date_debut = django_filters.TimeRangeFilter(label='date de début')
    # date_debut = django_filters.DateFilter(label='date de début')


    class Meta:
        model = Produit
        fields = ['categorie', 'user__username', 'nom_produit', "description", "prixmin","prixmax","date_debut"]
        # fields = {
        #      'categorie':['exact'],
        #     'nom_produit':['contains'],
        #     'description':['contains'],
        #     # 'date_creation': ['exact'],
        #     # 'date_debut': ['exact'],
        #     # 'date_expiration': ['exact'],
        #      'prix':['gte','lte'],
        # }




class Panier(models.Model):
    date_creation = models.DateTimeField(verbose_name=_('date de création '), editable=False)
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))

    etat = models.CharField(
        max_length=8,
        choices=(('a', 'en cours'),('ok', 'validé'), ('t', 'terminé'), ('c', 'annulé')),
        default='a', verbose_name="état"
    )

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = now()
        return super(Panier, self).save(*args, **kwargs)

    
    def __unicode__(self):
        return u'panier de %s' % (self.user.username) 
    
    class Meta:
        verbose_name = _('panier')
        verbose_name_plural = _('paniers')
        ordering = ('-date_creation',)

    def __iter__(self):
        for item in self.item_set.all():
            yield item

    def get_nom_class(self):
        return "Panier"


    def add(self, produit, unit_price, quantite=1):
        try:
            item = Item.objects.get(
                panier=self,
                produit=produit,
            )
        except Item.DoesNotExist:
            item = Item()
            item.panier = self
            item.produit = produit
            item.quantite = quantite
            item.save()
        else: #ItemAlreadyExists
            item.quantite += decimal.Decimal(quantite).quantize(decimal.Decimal('.001'), rounding=decimal.ROUND_HALF_UP)
            item.save()

    def remove(self, produit):
        try:
            item = Item.objects.get(
                panier=self,
                produit=produit,
            )
        except Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.delete()

    def remove_item(self, item_id):
        try:
            item = Item.objects.get(
                panier=self,
                id=item_id,
            )
        except Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.delete()

    def update(self, produit, quantite):
        try:
            item = Item.objects.get(
                panier=self,
                produit=produit,
            )
        except Item.DoesNotExist:
            raise ItemDoesNotExist
        else: #ItemAlreadyExists
            if quantite == 0:
                item.delete()
            else:
                item.quantite =  decimal.Decimal(quantite).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_UP)
                item.save()

    def total_quantite(self):
        result = {}
        for item in self.item_set.all():
            unite = item.produit.get_unite_prix()
            #type_prix = item.produit.get_type_prix()
            if not unite in result.keys():
                result[unite] = 0
            result[unite] += item.quantite
        return result


    def total_quantite_str(self):
        res = ""
        for unite_prix, qte in self.total_quantite().items():
            res += str(qte) +" "+ unite_prix +"; "
        return res

    def total_prix(self):
        result = {}
        for item in self.item_set.all():
            unite = item.produit.get_unite_prix()
            if not unite in result.keys():
                result[unite] = 0
            result[unite] += item.total_prix
        return result

    def total_prix_str(self):
        res = ""
        for unite_prix, prix in self.total_quantite().items():
            res += str(round (prix, 2)) +" "+ unite_prix +"; "
        return res

    def clear(self):
        for item in self.item_set.all():
            item.delete()

    total_prix_str = property(total_prix_str)
    total_quantite_str = property(total_quantite_str)

    def get_items_from_user(self, user_id):
        for item in self.item_set.all():
            if item.produit.user.id == user_id:
                yield item

    def get_message_demande(self, user_id):
        message= 'Bonjour, je suis intéressė par : \n'
        for item in self.get_items_from_user(user_id):
            message += "\t" + str(float(item.quantite)) + "\t" + str(item.produit.nom_produit)
            if item.total_prixEtunite != 0:
                message += " pour un total de " + str(item.total_prixEtunite)
            message        += ", \n"
        message += "Merci !"
        return message

class ItemManager(models.Manager):
    def get(self, *args, **kwargs):
        return super(ItemManager, self).get(*args, **kwargs)



class Item(models.Model):
    panier = models.ForeignKey(Panier, verbose_name=_('panier'), on_delete=models.CASCADE)
    quantite = models.DecimalField(verbose_name=_('quantite'),decimal_places=3,max_digits=6)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

    objects = ItemManager()

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('panier',)

    def __unicode__(self):
        return u'%s de %s' % (float(self.quantite), self.produit.nom_produit)

    def total_prix(self):
        if self.produit.unite_prix == 'don':
            return 0
        return self.quantite * self.produit.get_prix()

    def total_prixEtunite(self):
        if self.produit.unite_prix == 'don':
            return 0
        return str(round(self.quantite * self.produit.get_prix(),2)) +" "+ self.produit.unite_prix

    total_prix = property(total_prix)
    total_prixEtunite = property(total_prixEtunite)

#
# class Place(models_gis.Model):
#     ville = models_gis.CharField(max_length=255)
#     #location = spatial.LocationField(based_fields=['ville'], zoom=7, default=Point(1.0, 1.0))
#     location = spatial.PlainLocationField(based_fields=['ville'], zoom=7)
#     objects = models_gis.GeoManager()



def get_slug_from_names(name1, name2):
    return str(slugify(''.join(sorted((name1, name2), key=str.lower))))

class Conversation(models.Model):
    profil1 = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='profil1')
    profil2 = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='profil2')
    slug = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Date de parution")
    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)

    class Meta:
        ordering = ('-date_dernierMessage',)

    def __str__(self):
        return "Conversation entre " + self.profil1.username + " et " + self.profil2.username

    def titre(self):
        return self.__str__()

    titre = property(titre)

    @property
    def auteur_1(self):
        return self.profil1.username

    @property
    def auteur_2(self):
        return self.profil2.username

    @property
    def messages(self):
        return self.__str__()


    def get_absolute_url(self):
        return reverse('lireConversation_2noms', kwargs={'destinataire1': self.profil1.username, 'destinataire2': self.profil2.username})

    def save(self, *args, **kwargs):
        self.slug = get_slug_from_names(self.profil1.username, self.profil2.username)
        super(Conversation, self).save(*args, **kwargs)




def getOrCreateConversation(nom1, nom2):
    try:
        convers = Conversation.objects.get(slug=get_slug_from_names(nom1, nom2))
    except Conversation.DoesNotExist:
        profil_1 = Profil.objects.get(username=nom1)
        profil_2 = Profil.objects.get(username=nom2)
        convers = Conversation.objects.create(profil1=profil_1, profil2=profil_2)

        conversations = Conversation.objects.filter(Q(profil2=profil_1) | Q(profil1=profil_1))
        for conv in conversations:
            if conv in following(profil_1):
                actions.follow(profil_1, convers, send_action=False)
                break

        conversations = Conversation.objects.filter(Q(profil2=profil_2) | Q(profil1=profil_2))
        for conv in conversations:
            if conv in following(profil_2):
                actions.follow(profil_2, convers, send_action=False)
                break

    return convers


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.auteur) + " " + str(self.date_creation)

    @property
    def get_edit_url(self):
        return reverse('modifierMessage',  kwargs={'id':self.id, 'type_msg':'conversation', 'asso':'convers'})

    @property
    def get_absolute_url(self):
        return self.conversation.get_absolute_url()



class MessageGeneral(models.Model):
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.auteur) + " " + str(self.date_creation)

    @property
    def get_edit_url(self):
        return reverse('modifierMessage',  kwargs={'id':self.id, 'type_msg':'agora', 'asso':self.asso.abreviation})

    @property
    def get_absolute_url(self):
        return  reverse('agora', kwargs={'asso':self.asso.abreviation})


class Suivis(models.Model):
    nom_suivi = models.TextField(null=False, blank=False)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.nom_suivi)


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

    # def getArticles(self):
    #     if self.nom == "public":
    #         return Article.objects.filter(asso="0")
    #     if self.nom == "permacat":
    #         return Article.objects.filter(asso="1")
    #     elif self.nom == "rtg":
    #         return Article.objects.filter(asso="2")
    #     elif self.nom == "ame":
    #         return Article.objects.filter(asso="3")