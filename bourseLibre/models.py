# -*- coding: utf-8 -*-
import decimal
import math
import os
import itertools
from datetime import date

import django_filters
import requests
from actstream import actions, action
from actstream.models import following, followers
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from model_utils.managers import InheritanceManager
from django.core.mail import send_mail
from .constantes import Choix, DEGTORAD
from .settings.production import SERVER_EMAIL
import simplejson
from datetime import datetime

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
    commune = models.CharField(max_length=50, blank=True, null=True, default="")
    latitude = models.FloatField(blank=True, null=True, default=LATITUDE_DEFAUT)
    longitude = models.FloatField(blank=True, null=True, default=LONGITUDE_DEFAUT)
    pays = models.CharField(max_length=12, blank=True, null=True, default="France")
    telephone = models.CharField(max_length=15, blank=True)


    def save(self, recalc=False, *args, **kwargs):
        ''' On save, update timestamps '''
        if recalc or not self.latitude or self.latitude == LATITUDE_DEFAUT:
            self.set_latlon_from_adresse()
        return super(Adresse, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('profil_courant')

    def __str__(self):
        if self.commune:
            return "("+str(self.id)+") " + self.commune
        else:
            return "("+str(self.id)+") "+self.code_postal


    def getDistance(self, adresse):
        try:
            x1 = float(self.latitude)*DEGTORAD
            y1 = float(self.longitude)*DEGTORAD
            x2 = float(adresse.latitude)*DEGTORAD
            y2 = float(adresse.longitude)*DEGTORAD
            x = (y2-y1) * math.cos((x1+x2)/2)
            y = (x2-x1)

            return math.sqrt(x*x + y*y) * 6371
        except:
            return 0

    @property
    def get_adresse_str(self):
        if self.commune:
            adress = ''
            if self.rue:
                adress += self.rue
            if self.code_postal:
                adress += ", " + self.code_postal
            if self.commune:
                adress += ", " + self.commune
            if self.telephone:
                adress += " (" + self.telephone +")"
            return adress
        else:
            return str(self.latitude) + ", " + str(self.longitude)

    def __unicode__(self):
        return self.__str__()

    def set_latlon_from_adresse(self):
        address = ''
        if self.rue:
            address += self.rue + "+"
        address += str(self.code_postal)
        if self.commune:
            address += "+" + self.commune
        address = address.replace(" ", "+")

        try:
            url = "http://nominatim.openstreetmap.org/search?q=" + address + "&format=json"
            reponse = requests.get(url)
            data = simplejson.loads(reponse.text)
            self.latitude = float(data[0]["lat"])
            self.longitude = float(data[0]["lon"])
        except:
            try:
                address = str(self.code_postal)
                if self.commune:
                    address += "+" + self.commune
                address = address.replace(" ", "+")
                url = "http://nominatim.openstreetmap.org/search?q=" + address + "&format=json"
                reponse = requests.get(url)
                data = simplejson.loads(reponse.text)
                self.latitude = float(data[0]["lat"])
                self.longitude = float(data[0]["lon"])
            except:
                try:
                    api_key = os.environ["GAPI_KEY"]
                    api_response = requests.get(
                        'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
                    api_response_dict = api_response.json()

                    if api_response_dict['status'] == 'OK':
                        self.latitude = float(api_response_dict['results'][0]['geometry']['location']['lat'])
                        self.longitude = float(api_response_dict['results'][0]['geometry']['location']['lng'])
                except:
                    self.latitude = LATITUDE_DEFAUT
                    self.longitude = LONGITUDE_DEFAUT

        self.save()

    def get_latitude(self):
        if not self.latitude:
            return LATITUDE_DEFAUT
        return str(self.latitude).replace(",",".")

    def get_longitude(self):
        if not self.longitude:
            return LONGITUDE_DEFAUT
        return str(self.longitude).replace(",",".")

    def getLatLon(self):
        return str(self.latitude) + ", " + str(self.longitude)

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
        if self.abreviation == "public":
            return True
        if not getattr(user, "adherent_" + self.abreviation):
            return False
        return True

    def getProfils_cotisationAJour(self):
        return [p for p in self.getProfils() if p.isCotisationAJour(self.abreviation)]

    def getProfils(self):
        if self.abreviation == "public":
            return Profil.objects.all().order_by("username")
        elif self.abreviation == "pc":
            return Profil.objects.filter(adherent_pc=True).order_by("username")
        elif self.abreviation == "rtg":
            return Profil.objects.filter(adherent_rtg=True).order_by("username")
        elif self.abreviation == "fer":
            return Profil.objects.filter(adherent_fer=True).order_by("username")
        #elif self.abreviation == "gt":
        #    return Profil.objects.filter(adherent_gt=True).order_by("username")
        elif self.abreviation == "scic":
            return Profil.objects.filter(adherent_scic=True).order_by("username")
        elif self.abreviation == "citealt":
            return Profil.objects.filter(adherent_citealt=True).order_by("username")
        elif self.abreviation == "bzz2022":
            return Profil.objects.filter(adherent_bzz2022=True).order_by("username")
        elif self.abreviation == "viure":
            return Profil.objects.filter(adherent_viure=True).order_by("username")
        return []

    def getProfils_Annuaire(self):
        if self.abreviation == "public":
            return Profil.objects.filter(accepter_annuaire=True).order_by("username")
        elif self.abreviation == "pc":
            return Profil.objects.filter(accepter_annuaire=True, adherent_pc=True).order_by("username")
        elif self.abreviation == "rtg":
            return Profil.objects.filter(accepter_annuaire=True, adherent_rtg=True).order_by("username")
        elif self.abreviation == "fer":
            return Profil.objects.filter(accepter_annuaire=True, adherent_fer=True).order_by("username")
        #elif self.abreviation == "gt":
        #    return Profil.objects.filter(accepter_annuaire=True, adherent_gt=True).order_by("username")
        elif self.abreviation == "scic":
            return Profil.objects.filter(accepter_annuaire=True, adherent_scic=True).order_by("username")
        elif self.abreviation == "citealt":
            return Profil.objects.filter(accepter_annuaire=True, adherent_citealt=True).order_by("username")
        elif self.abreviation == "viure":
            return Profil.objects.filter(accepter_annuaire=True, adherent_viure=True).order_by("username")
        elif self.abreviation == "bzz2022":
            return Profil.objects.filter(accepter_annuaire=True, adherent_bzz2022=True).order_by("username")
        return []


    def get_absolute_url(self):
        return reverse_lazy('presentation_asso', asso=self.abreviation)


    @property
    def get_logo_nomgroupe(self):
        from blog.models import Choix as Choix_asso
        return Choix_asso.get_logo_nomgroupe(self.abreviation)

    @property
    def get_logo_nomgroupe_html(self):
        return self.get_logo_nomgroupe_html_taille()

    def get_logo_nomgroupe_html_taille(self, taille=25):
        return "<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

class Profil(AbstractUser):
    username_validator = ASCIIUsernameValidator()
    site_web = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    competences = models.TextField(null=True, blank=True)
    adresse = models.OneToOneField(Adresse, on_delete=models.CASCADE)
    #avatar = StdImageField(null=True, blank=True, upload_to='avatars/', variations={
    #    'large': (640, 480),
    #    'thumbnail2': (100, 100, True)})

    date_registration = models.DateTimeField(verbose_name="Date de création", editable=False)
    pseudo_june = models.CharField(_('pseudo Monnaie Libre'), blank=True, default=None, null=True, max_length=50)

    inscrit_newsletter = models.BooleanField(verbose_name="J'accepte de recevoir des emails de Perma.cat", default=False)
    #statut_adhesion = models.IntegerField(choices=Choix.statut_adhesion, default="0")
    adherent_pc = models.BooleanField(verbose_name="Je suis adhérent de Permacat", default=False)
    adherent_rtg = models.BooleanField(verbose_name="Je suis adhérent de Ramene Ta Graine", default=False)
    adherent_fer = models.BooleanField(verbose_name="Je suis adhérent de Fermille", default=False)
    #adherent_gt = models.BooleanField(verbose_name="Je suis adhérent de Gardiens de la Terre", default=False)
    adherent_scic = models.BooleanField(verbose_name="Je suis intéressé par le collectif 'PermAgora'", default=False)
    adherent_citealt = models.BooleanField(verbose_name="Je fais partie de 'la Cité Altruiste'", default=False)
    adherent_viure = models.BooleanField(verbose_name="Je fais partie du collectif 'Viure'", default=False)
    adherent_bzz2022 = models.BooleanField(verbose_name="Je fais partie du collectif 'Bzzz'", default=False)
    accepter_conditions = models.BooleanField(verbose_name="J'ai lu et j'accepte les conditions d'utilisation du site", default=False, null=False)
    accepter_annuaire = models.BooleanField(verbose_name="J'accepte d'apparaitre dans l'annuaire du site et la carte et rend mon profil visible par tous", default=True)
    adherent_jp = models.BooleanField(verbose_name="Je suis intéressé.e par les jardins partagés", default=False)

    date_notifications = models.DateTimeField(verbose_name="Date de validation des notifications",default=now)
    afficherNbNotifications = models.BooleanField(verbose_name="Affichage du nombre de notifications dans le menu", default=False)


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
        return self.adresse.getDistance(profil.adresse)

    def getAdhesions(self, abreviationAsso):
        if abreviationAsso == "pc" :
            return Adhesion_permacat.objects.filter(user=self)
        else:
            return Adhesion_asso.objects.filter(user=self, asso__abreviation=abreviationAsso)

    def isCotisationAJour(self, asso_abreviation):
        time_threshold = datetime(datetime.now().year - 1, 11, 1)
        return self.getAdhesions(asso_abreviation).filter(date_cotisation__gt=time_threshold).count() > 0


    @property
    def isCotisationAJour_pc(self):
        return self.isCotisationAJour("pc")

    @property
    def isCotisationAJour_scic(self):
        return self.isCotisationAJour("scic")

    @property
    def statutMembre_asso(self, asso):
        if asso == "permacat" or "pc":
            return self.adherent_pc
        elif asso == "rtg":
            return self.adherent_rtg
        elif asso == "fer":
            return self.adherent_fer
        elif asso == "jp":
            return self.adherent_jp
        elif asso == "scic":
            return self.adherent_scic
        elif asso == "citealt":
            return self.adherent_citealt
        elif asso == "viure":
            return self.adherent_viure
        elif asso == "bzz2022":
            return self.adherent_bzz2022


    @property
    def statutMembre_str_asso(self, asso):
        if asso == "permacat":
            if self.adherent_pc:
                return "membre actif de Permacat"
            else:
                return "Non membre de Permacat"
        if asso == "rtg":
            if self.adherent_rtg:
                return "membre actif de 'Ramene Ta Graine'"
            else:
                return "Non membre de 'Ramene Ta Graine'"
        if asso == "fer":
            if self.adherent_fer:
                return "membre actif de 'Fermille'"
            else:
                return "Non membre de 'Fermille'"
        if asso == "jp":
            if self.adherent_jp:
                return "membre actif des 'Jardins Partagés'"
            else:
                return "Non membre des 'Jardins Partagés'"
        if asso == "scic":
            if self.adherent_scic:
                return "membre actif de 'PermAgora'"
            else:
                return "Non membre de 'PermAgora'"
        if asso == "citealt":
            if self.adherent_citealt:
                return "membre actif de la 'Cité Altruiste'"
            else:
                return "Non membre de la 'Cité Altruiste'"
        if asso == "viure":
            if self.adherent_viure:
                return "membre actif du Collectif Viure'"
            else:
                return "Non membre du Collectif Viure'"
        if asso == "bzz2022":
            if self.adherent_bzz2022:
                return "membre actif du Collectif Bzzz'"
            else:
                return "Non membre du Collectif Bzzz'"

    def estMembre_str(self, nom_asso):
        if nom_asso == "Public" or nom_asso == "public":
            return True
        elif self.adherent_pc and(nom_asso == "Permacat" or nom_asso == "pc") :
            return True
        elif self.adherent_rtg and (nom_asso == "Ramène Ta Graine" or nom_asso == "rtg") :
            return True
        elif self.adherent_fer and (nom_asso == "Fermille" or nom_asso == "fer") :
            return True
        elif self.adherent_scic and (nom_asso == "PermAgora" or nom_asso == "scic") :
            return True
        elif self.adherent_citealt and (nom_asso == "Cité Altruiste" or nom_asso == "citealt") :
            return True
        elif self.adherent_viure and (nom_asso == "Viure" or nom_asso == "viure") :
            return True
        elif self.adherent_bzz2022 and (nom_asso == "bzz2022" or nom_asso == "bzz2022") :
            return True
        #elif self.adherent_gt and (nom_asso == "Gardiens de la Terre" or nom_asso == "gt") :
        #    return True
        else:
            return False

    def getQObjectsAssoArticles(self):
        q_objects = Q()
        for asso in self.getListeAbreviationsAssosEtPublic():
            q_objects |= Q(asso__abreviation=asso) | Q(partagesAsso__abreviation=asso)
        return q_objects

    def getListeAbreviationsAssos(self):
        return [a for a in Choix.abreviationsAsso if self.est_autorise(a)]

    def getListeAbreviationsAssosEtPublic(self):
        return ["public", ] + [a for a in Choix.abreviationsAsso if self.est_autorise(a)]

    def est_autorise(self, abreviation_asso):
        if abreviation_asso == "public":
            return True

        return getattr(self, "adherent_" + abreviation_asso)

    @property
    def inscrit_newsletter_str(self):
       return "oui" if self.inscrit_newsletter else "non"

    @property
    def a_signe_permagora(self):
        from permagora.models import Signataire
        return Signataire.objects.filter(auteur=self).exists()

def envoyerMailBienvenue(user):
    titre = "[Permacat] Inscription sur le site"
    pseudo = user.username
    messagetxt = "Bienvenue sur www.Perma.Cat ! Pour vous connecter, votre identifiant est : (vous pouvez le changer sur votre page de profil), merci de votre inscription. \
    Voici quelques conseils : pour suivre ce qu'il se passe sur le site, utilisez les notifications (et n'oubliez pas d'appuyer sur 'marquer comme lu' après les avoir lu). l'agenda est un bon moyen de savoir ce qu'il se passe dans la vraie vie, visuellement.\
    utilisez plutot l'altermarché pour les petites annonces, le forum pour annoncer les événements ou présenter des idées, et les ateliers pour... proposer des ateliers\
    vous pouvez configurer les infos que vous recevez par mail sur la page abonnements de votre profil\
    prenez le temps d'explorer les différentes sections du site pour vous familiariser et comprendre comment le site fonctionne et ce que vous pouvez en faire\
    sur smartphone, vous pouvez mettre le site sur votre page d'accueil pour y accéder facilement et venir nous voir plus régulièrement.\
    en toute circonstance, gardez le sourire :)\
    pour toute question, consultez la Foire Aux Questions (ou posez vos questions dans l'article consacré). @ bientôt !"
    message = "<div dir='auto'>Bienvenue sur www.Perma.Cat ! merci de votre inscription :)</div> \
<div dir='auto'>&nbsp;</div>\
<div dir='auto'>Pour vous connecter, votre identifiant est : "+user.username+" (attention, les majuscules sont importantes).</div>\
<div dir='auto'>Vous pouvez changer votre pseudo ou vos infos personnelles sur votre <a href='https://www.perma.cat/accounts/profile/'>page de profil</a>)</div>\
<div dir='auto'>&nbsp;</div>\
<div dir='auto'>Quelques conseils :\
<ul>\
<li dir='auto'>pour suivre ce qu'il se passe sur le site, utilisez les <a href='https://www.perma.cat/notifications/activite/'>notifications</a> (et n'oubliez pas d'appuyer sur 'marquer comme lu' apres les avoir lu).</li>\
<li dir='auto'>l'<a href='https://www.perma.cat/agenda/'>agenda</a> est un bon moyen de savoir ce qu'il se passe dans la vraie vie, visuellement.</li>\
<li dir='auto'>l'<a href='https://www.perma.cat/annuaire/public'>annuaire</a> ou <a href='https://www.perma.cat/cooperateurs/carte/public'>la carte</a> sont de bons moyens de faire connaissance avec de belles personnes, près de chez vous</li>\
<li dir='auto'>utilisez plutôt l'<a href='https://www.perma.cat/marche/lister/'>altermarch&eacute;</a> pour les petites annonces, le <a href='https://www.perma.cat/forum/accueil/'>forum</a> pour annoncer les &eacute;v&eacute;nements ou pr&eacute;senter des id&eacute;es, et les <a href='https://www.perma.cat/ateliers/liste/'>ateliers</a> pour... proposer des ateliers</li>\
<li dir='auto'>vous pouvez configurer les infos que vous recevez par mail sur la page <a href='https://www.perma.cat/accounts/mesSuivis/'>abonnements</a> de votre profil</li>\
<li dir='auto'>prenez le temps d'explorer les diff&eacute;rentes sections du site pour vous familiariser et comprendre comment le site fonctionne et ce que vous pouvez en faire</li>\
<li dir='auto'>sur smartphone, vous pouvez <a href='https://www.clubic.com/tutoriels/article-891621-1-comment-ajouter-raccourci-web-page-accueil-smartphone-android.html'>mettre le site sur votre page d'accueil</a> pour y acc&eacute;der facilement et venir nous voir plus r&eacute;guli&egrave;rement.</li>\
<li dir='auto'>gardez le sourire :)</li></ul>\
<div dir='auto'>&nbsp;</div>\
<div dir='auto'>pour toute question, consultez la <a href='https://www.perma.cat/faq/'>Foire Aux Questions</a> (<span style='font-family: sans-serif;'>ou <a href='https://www.perma.cat/forum/article/faq-du-site'>posez</a></span><a href='https://www.perma.cat/forum/article/faq-du-site'> vos questions dans l'article consacr&eacute;</a>).</div>\
<div dir='auto'>&nbsp;</div>\
<div dir='auto'>@ bient&ocirc;t !</div>\
</div>"
    from bourseLibre.settings.production import LOCALL
    if not LOCALL:
        send_mail(titre, messagetxt,
                  SERVER_EMAIL, [user.email, SERVER_EMAIL], fail_silently=False,
                  html_message=message)


@receiver(post_save, sender=Profil)
def create_user_profile(sender, instance, created, **kwargs):
    if created :
        if instance.inscrit_newsletter:
            for suiv in Choix.suivisPossibles:
                suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)
                actions.follow(instance, suivi, actor_only=True, send_action=False)
            for abreviation in Choix.abreviationsAsso + ['public', ]:
                if instance.est_autorise(abreviation):
                    suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_"+abreviation)
                    actions.follow(instance, suivi, actor_only=True, send_action=False)
                    suivi, created = Suivis.objects.get_or_create(nom_suivi="agora_"+abreviation)
                    actions.follow(instance, suivi, actor_only=True, send_action=False)
                    suivi, created = Suivis.objects.get_or_create(nom_suivi="salon_accueil")
                    actions.follow(instance, suivi, actor_only=True, send_action=False)
        action.send(instance, verb='inscription', url=instance.get_absolute_url(),
                    description="s'est inscrit.e sur le site")
        envoyerMailBienvenue(instance)
        if instance.is_superuser:
            Panier.objects.create(user=instance)


class Adhesion_permacat(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE, verbose_name="Utilisateur Permacat")
    date_cotisation = models.DateField(verbose_name="Date de la cotisation", editable=True, auto_now_add=False)
    montant = models.CharField(max_length=50, blank=False, verbose_name="Montant de l'adhesion")
    moyen = models.CharField(
        max_length=3,
        choices=Choix.type_paiement_adhesion,
        default='0', verbose_name="Moyen de maiement"
    )

    def __str__(self):
        return self.user.username + " le "+ str(self.date_cotisation) + " " + str(self.montant) + " " + str(self.moyen)

class Adhesion_asso(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE, verbose_name="Utilisateur ")
    date_cotisation = models.DateField(verbose_name="Date de la cotisation", editable=True, auto_now_add=False)
    montant = models.CharField(max_length=50, blank=False, verbose_name="Montant de l'adhesion")
    moyen = models.CharField(
        max_length=3,
        choices=Choix.type_paiement_adhesion,
        default='0', verbose_name="Moyen de maiement"
    )
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username + " le " + str(self.date_cotisation) + " " + str(self.montant) + " " + str(self.moyen) + "(" + self.asso.nom + ")"

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
        choices=Choix.monnaies,
        default='lliure', verbose_name="monnaie"
    )

    CHOIX_CATEGORIE = (('aliment', 'aliment'),('vegetal', 'végétal'), ('service', 'service'), ('objet', 'objet'), ('liste', 'liste des offres et demandes'))
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
            if self.categorie=='liste':
                message = "Nouvelle liste d'offres et demandes : [" + self.asso.nom + "] <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.nom_produit + "</a>"
            else:
                if self.estUneOffre:
                    message = "Nouvelle petite annonce (offre) : ["+ self.asso.nom +"] <a href='https://www.perma.cat" + self.get_absolute_url() +"'>" + self.nom_produit + "</a>"
                else:
                    message = "Nouvelle petite annonce (demande) : ["+ self.asso.nom +"] <a href='https://www.perma.cat" + self.get_absolute_url() +"'>" + self.nom_produit + "</a>"
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour


    @property
    def absolute_url(self):
        return self.get_absolute_url()

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
        prod_cat = Produit.objects.get_subclass(id=self.id)
        if isinstance(prod_cat, Produit):
            return str(self.get_prix()) + " " + self.get_unite_prix()
        return prod_cat.get_prixEtUnite()

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

        return getattr(user, "adherent_" + self.asso.abreviation)

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

class Produit_offresEtDemandes(Produit):  # , BaseProduct):
    type = 'offresEtDemandes'
    couleur = models.CharField(
        max_length=20,
        choices=((Choix.couleurs['offresEtDemandes'], Choix.couleurs['offresEtDemandes']),),
        default=Choix.couleurs['offresEtDemandes']
    )
    souscategorie = models.CharField(
        max_length=20,
        choices=((cat, cat) for cat in Choix.choix[type]['souscategorie']),
        default=Choix.choix[type]['souscategorie'][0]
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
        return "offresEtDemandes"

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
    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=False, blank=True, null=True)
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

    return convers


class Salon(models.Model):
    titre = models.CharField(max_length=250)
    auteur = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Date de parution")
    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=False, blank=True, null=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    membres = models.ManyToManyField(Profil, through='InscritSalon')
    estPublic = models.BooleanField(verbose_name="Salon public ou privé (public si coché)", default=False)
    article = models.ForeignKey("blog.Article", on_delete=models.CASCADE,
                                help_text="Le salon doit être associé à un article existant (sinon créez un article avec une date)", blank=True, null=True)

    #asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ('titre',)

    def __str__(self):
        return "Salon '" + self.titre + "'"

    def get_absolute_url(self):
        return reverse('salon', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        max_length = 99
        if not self.id:
            self.slug = orig = slugify(self.titre)[:max_length]

            for x in itertools.count(1):
                if not Salon.objects.filter(slug=self.slug).exists():
                    break

                # Truncate the original slug dynamically. Minus 1 for the hyphen.
                self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

            self.date_creation = now()

        super(Salon, self).save(*args, **kwargs)


    def est_autorise(self, user):
        return self.estPublic or user in self.membres.all()

    def getInscrits(self):
        return [u.profil for u in InscritSalon.objects.filter(salon=self)]

    def getInvites(self):
        return [u.profil_invite for u in InvitationDansSalon.objects.filter(salon=self)]

class InscritSalon(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(verbose_name="Date de création", editable=False, auto_now_add=True)

class InvitationDansSalon(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    profil_invitant = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="invitant")
    profil_invite = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="invite")
    date_creation = models.DateTimeField(verbose_name="Date de création", editable=False, auto_now_add=True)

    def __str__(self):
        return " "
    @property
    def texte(self):
        return "%s a invité %s dans le salon %s" %(self.profil_invitant, self.profil_invite, self.salon.titre)

    class Meta:
        unique_together = (('profil_invitant', 'profil_invite', 'salon'), )


    def save(self, *args, **kwargs):
        super(InvitationDansSalon, self).save(*args, **kwargs)
        emails = [self.profil_invite.email, ]
        message = "Vous avez été invité.e au salon de discussion : <a href='https://www.perma.cat/'%s'>'%s'</a>" % (self.salon.get_absolute_url(), self.salon.titre)
        action.send(self, verb='emails', url=self.salon.get_absolute_url(), titre=self.salon.titre, message=message, emails=emails)

        message = "Vous avez été invité.e au salon de discussion : <a href='https://www.perma.cat/'%s'>'%s'</a>" % (self.salon.get_absolute_url(), self.salon.titre)
        action.send(self, verb='invitation_salon', url=self.salon.get_absolute_url(), titre=self.salon.titre, message=message, description="%s a été invité dans le salon %s : " %(self.profil_invite, self.salon.titre, ))

    def get_absolute_url(self):
        return self.salon.get_absolute_url()


class Message_salon(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    message = models.TextField(null=False, blank=False)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.auteur) + " " + str(self.date_creation)

    @property
    def get_edit_url(self):
        return reverse('modifierMessage',  kwargs={'id':self.id, 'type_msg':'salon', 'asso':'None'})

    def get_absolute_url(self):
        return self.salon.get_absolute_url()

    def save(self, *args, **kwargs):
        super(Message_salon, self).save(*args, **kwargs)
        self.salon.date_dernierMessage = now()
        self.salon.save()

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

    def get_absolute_url(self):
        return self.conversation.get_absolute_url()


    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        self.conversation.date_dernierMessage = now()
        self.conversation.save()


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

    def get_absolute_url(self):
        return reverse('agora', kwargs={'asso':self.asso.abreviation})

    def save(self,):
        suivis, created = Suivis.objects.get_or_create(nom_suivi='agora_' + str(self.asso.abreviation))
        emails = [suiv.email for suiv in followers(suivis) if self.auteur != suiv and self.est_autorise(suiv)]
        titre = "Nouveau commentaire dans le salon de discussion " + str(self.asso.nom)
        message = "Nouveau commentaire dans <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" +"le salon de discussion " + str(self.asso.nom) +  "</a>'"

        if emails:
            action.send(self.auteur, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)

        return super(MessageGeneral, self).save()

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True

        return getattr(user, "adherent_" + self.asso.abreviation)

class Suivis(models.Model):
    nom_suivi = models.TextField(null=False, blank=False)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.nom_suivi)

    def get_absolute_url(self):
        return ""

#class Gestionnaire_Suivis():
        #    def get_suivi_articles(self, asso):
        #suivis, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(asso.abreviation))
        #return suivis


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