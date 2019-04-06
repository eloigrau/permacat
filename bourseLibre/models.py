# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User#, AbstractUser
#from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.utils.timezone import now
# from django.utils.formats import localize
#from address.models import AddressField
import datetime
from model_utils.managers import InheritanceManager
import django_filters
from django.urls import reverse, reverse_lazy
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify

from django.utils.translation import ugettext_lazy as _
#from django.contrib., contenttypes.models import ContentType
import decimal, math

import os
import requests
from stdimage import StdImageField
from datetime import date

# from location_field.models import spatial

#from django.contrib.gis.db import models as models_gis
# from django.contrib.gis.geos import Point
#from geoposition.fields import GeopositionField

#from django.contrib.gis.db.models import GeoManager

class Choix():
    #couleurs = {'aliment':'#D8C457','vegetal':'#4CAF47','service':'#BE373A','objet':'#5B4694'}
    #couleurs = {'aliment':'#80B2C0','vegetal':'#A9CB52','service':'#E66562','objet':'#D8AD57'}
    couleurs = {'aliment':'#e6f2ff','vegetal':'#e6ffe6','service':'#ffe6e6','objet':'#ffffe6'}
    typePrixUnite =  (('kg', 'kg'), ('100g', '100g'), ('10g', '10g'),('g', 'g'),  ('un', 'unité'), ('li', 'litre'))

    choix = {
    'aliment': {
        'souscategorie': ('legumes', 'fruits', 'aromates', 'champignons', 'boisson', 'herbes', 'condiments', 'viande', 'poisson', 'boulangerie', 'patisserie', 'autre'),
        #'etat': (('frais', 'frais'), ('sec', 'sec'), ('conserve', 'conserve')),
        'type_prix': typePrixUnite,
    },
    'vegetal': {
        'souscategorie': ('plantes', 'graines', 'fleurs', 'jeunes plants', 'purins', 'autre', ),
        #'etat': (('frais', 'frais'), ('séché', 'séché')),
        'type_prix': typePrixUnite,
    },
    'service': {
        'souscategorie': ('jardinage',  'éducation', 'santé', 'bricolage', 'informatique', 'cuisine','batiment', 'mécanique', 'autre'),
        #'etat': (('excellent', 'excellent'), ('bon', 'bon'), ('moyen', 'moyen'), ('naze', 'naze')),
        'type_prix': (('h', 'heure'), ('un', 'unité')),
    },
    'objet': {
        'souscategorie': ('jardinage', 'outillage', 'vehicule', 'multimedia', 'mobilier','construction','instrument','autre'),
        #'etat': (('excellent', 'excellent'), ('bon', 'bon'), ('moyen', 'moyen'), ('mauvais', 'mauvais')),
        'type_prix': typePrixUnite,
    },
    }
    monnaies = (('don', 'don'), ('troc', 'troc'), ('pret', 'pret'), ('G1', 'G1'), ('soudaqui', 'soudaqui'), ('SEL', 'SEL'), ('JEU', 'JEU'),  ('heuresT', 'heuresT'),  ('Autre', 'A negocier'))
    monnaies_nonquantifiables =['don', 'troc', 'pret', 'SEl']

    ordreTri = ['date', 'categorie', 'producteur']
    distances = ['5', '10', '20', '30', '50', '100']

    statut_adhesion = (('', '-----------'),
                     (0, _("Je souhaite devenir membre de l'association 'PermaCat' et utiliser le site")),
                    (1, _("Je souhaite utiliser le site, mais ne pas devenir membre de l'association")),
                    (2, _("Je suis déjà membre de l'association")))


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


class Profil(AbstractUser):

    site_web = models.URLField(null=True, blank=True)
    description = models.TextField(null=True)
    competences = models.TextField(null=True)
    adresse = models.OneToOneField(Adresse, on_delete=models.CASCADE)
    avatar = StdImageField(null=True, blank=True, upload_to='avatars/', variations={
        'large': (640, 480),
        'thumbnail2': (100, 100, True)})

    date_registration = models.DateTimeField(verbose_name="Date de création", editable=False)
    pseudo_june = models.CharField(_('pseudo Monnaie Libre'), blank=True, default=None, null=True, max_length=50)

    inscrit_newsletter = models.BooleanField(verbose_name="J'accepte de recevoir des emails de Permacat", default=False)
    statut_adhesion = models.IntegerField(choices=Choix.statut_adhesion, default="0")
    accepter_conditions = models.BooleanField(verbose_name="J'ai lu et j'accepte les conditions d'utilisation du site", default=False, null=False)

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
        return reverse('profil_courant')#, kwargs={'user_id':self.id})

    def getDistance(self, profil):
        degtorad=3.141592654/180
        x1 = float(self.adresse.latitude)*degtorad
        y1 = float(self.adresse.longitude)*degtorad
        x2 = float(profil.adresse.latitude)*degtorad
        y2 = float(profil.adresse.longitude)*degtorad
        x = (y2-y1) * math.cos((x1+x2)/2)
        y = (x2-x1)
        return math.sqrt(x*x + y*y) * 6371

    @property
    def statutMembre(self):
        return self.statut_adhesion

    @property
    def statutMembre_str(self):
        if self.statut_adhesion == 0:
            return "souhaite devenir membre de l'association"
        elif self.statut_adhesion == 1:
            return "ne souhaite pas devenir membre"
        elif self.statut_adhesion == 2:
            return "membre actif"

    @property
    def is_permacat(self):
        if self.statut_adhesion == 2:
            return True
        else:
            return False
    
@receiver(post_save, sender=Profil)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Panier.objects.create(user=instance)
    elif created:
        instance.is_active=False


#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.profil.save()



class Produit(models.Model):  # , BaseProduct):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE,)
    date_creation = models.DateTimeField(verbose_name="Date de parution", editable=False)
    date_debut = models.DateField(verbose_name="Débute le : (jj/mm/an)", null=True, blank=True)
    #proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
    date_expiration = models.DateField(verbose_name="Expire le : (jj/mm/an)", blank=True, null=True, )#default=proposed_renewal_date, )
    nom_produit = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100)

    stock_initial = models.FloatField(default=1, verbose_name="Quantité disponible", max_length=250, validators=[MinValueValidator(1), ])
    stock_courant = models.FloatField(default=1, max_length=250, validators=[MinValueValidator(0), ])
    prix = models.DecimalField(max_digits=4, decimal_places=2, default=0, blank=True)#, validators=[MinValueValidator(0), ])
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
        if not self.id:
            self.date_creation = now()
            self.stock_courant = self.stock_initial
        return super(Produit, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('produit_detail', kwargs={'produit_id':self.id})

    def get_type_prix(self):
        return Produit.objects.get_subclass(id=self.id).type_prix

    def get_unite_prix(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.unite_prix
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
        return "bonjour, concernant ton annonce de '" + self.nom_produit + "', peux-tu m'indiquer..."


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
            return self.unite_prix
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
            return self.unite_prix
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
            return self.unite_prix
        else:
            return self.unite_prix + "/" + self.get_type_prix_display()

    def get_prixEtUnite(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.unite_prix
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
            return self.unite_prix
        else:
            return self.unite_prix + "/" + self.get_type_prix_display()

    def get_prixEtUnite(self):
        if self.unite_prix in Choix.monnaies_nonquantifiables:
            return self.unite_prix
        return str(self.get_prix()) + " " + self.get_unite_prix()

    def get_souscategorie(self):
        return "objet"

class ItemAlreadyExists(Exception):
    pass

class ItemDoesNotExist(Exception):
    pass

# from rest_framework import serializers
# class ProduitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Produit
#         fields = ('categorie','nom_produit','description','prix')


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

    def __unicode__(self):
        #return unicode(self.date_creation)
        return self.date_creation

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
            message += "\t" + str(item.quantite) + "\t" + str(item.produit.nom_produit)
            if item.total_prixEtunite != 0:
                message += " pour un total de " + str(item.total_prixEtunite)
            message        += ", \n"
        message += "Merci !"
        return message

class ItemManager(models.Manager):
    def get(self, *args, **kwargs):
        # if 'produit' in kwargs:
        #     kwargs['produit'] = Produit.objects.get(type(kwargs['produit'])).select_subclasses()
        #     kwargs['object_id'] = kwargs['produit'].pk
        #     del(kwargs['produit'])
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
        return u'%s de %s' % (self.quantite, self.produit.nom_produit)

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

    class Meta:
        ordering = ('-date_dernierMessage',)

    def __str__(self):
        return "Conversation entre " + self.profil1.username + " et " + self.profil2.username

    def titre(self):
        return self.__str__()

    titre = property(titre)

    @property
    def auteur_1(self):
        return "Conversation avec " + self.profil1.username

    @property
    def auteur_2(self):
        return "Conversation avec " + self.profil2.username

    @property
    def messages(self):
        return self.__str__()


    def get_absolute_url(self):
        return reverse('lireConversation_2noms', kwargs={'destinataire1': self.profil1.username, 'destinataire2': self.profil2.username})

    def save(self, *args, **kwargs):
        self.slug = get_slug_from_names(self.profil1.username, self.profil2.username)
        super(Conversation, self).save(*args, **kwargs)



class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message

class MessageGeneral(models.Model):
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message




def getOrCreateConversation(nom1, nom2):
    try:
        convers = Conversation.objects.get(slug=get_slug_from_names(nom1, nom2))
    except Conversation.DoesNotExist:
        profil_1 = Profil.objects.get(username=nom1)
        profil_2 = Profil.objects.get(username=nom2)
        convers = Conversation.objects.create(profil1=profil_1, profil2=profil_2)
    return convers
