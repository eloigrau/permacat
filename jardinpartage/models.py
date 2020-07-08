from django.db import models
from bourseLibre.models import Profil, Suivis
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mass_mail, mail_admins
#from tinymce.models import HTMLField
from django.dispatch import receiver
from django.db.models.signals import post_save

from actstream.models import followers
from bourseLibre.settings import SERVER_EMAIL

class Choix():
    type_annonce = ('Discu','Information'), ('Organisation', 'Organisation'), \
                  ('Potager','Au potager'), ('PPAM','PPAM'), ('Arbres','Les arbres au jardin'), \
                  ('Agenda','Agenda'), ("todo", "A faire"), \
                   ('Documentation','Documentation'),  \
                 ('Autre','Autre'),
    couleurs_annonces = {
       # 'Annonce':"#e0f7de", 'Administratif':"#dcc0de", 'Agenda':"#d4d1de", 'Entraide':"#cebacf",
       # 'Chantier':"#d1ecdc",'Jardinage':"#fcf6bd", 'Recette':"#d0f4de", 'Bricolage':"#fff2a0",
       # 'Culture':"#ffc4c8", 'Bon_plan':"#bccacf", 'Point':"#87bfae", 'Autre':"#bcb4b4"

        'Discu':"#d1ecdc",
        'Coordination':"#D4CF7D",
        'Agenda':"#E0E3AB",
        'Potager':"#AFE4C1",
        'PPAM':"#fff2a0",
        'Arbres':"#B2AFE4",
        'Administratif':"#d0f4de",
        'KitPerma':"#caf9b7",
        'Permaculture':"#ced2d3",
        'Documentation':"#349D9B",
        'Point':"#bccacf",
        'Autre':"#87bfae",
        'Ecovillage':"#cebacf",
        'Jardin':"#fffdcc",
        'Altermarché':"#daffb3",
        'aa':'#ddd0a8',



    }

    def get_couleur(categorie):
        try:
            return Choix.couleurs_annonces[categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_annonce),
        default='Discu', verbose_name="categorie")
    titre = models.CharField(max_length=100,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_article_jardin')
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres permacat')
    estModifiable = models.BooleanField(default=False, verbose_name="Modifiable par n'importe qui")

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'article")

    start_time = models.DateTimeField(verbose_name="Date de début (optionnel, affichage dans l'agenda)", null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        ordering = ('-date_creation', )
        db_table = 'article_jardin'

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('jardinpartage:lireArticle', kwargs={'slug':self.slug})


    def save(self, sendMail=True, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
            if sendMail:
                suivi, created = Suivis.objects.get_or_create(nom_suivi='articles')
                titre = "[Permacat-JardinPartagé] nouvel article"
                message = " Un nouvel article a été créé : https://permacat.herokuapp.com" + self.get_absolute_url() + \
                          "\n\n------------------------------------------------------------------------------" \
                          "\n vous recevez cet email, car vous avez choisi de suivre les articles (en cliquant sur la cloche) sur le site http://www.Perma.Cat/jardins/articles/"
                emails = [suiv.email for suiv in followers(suivi) if
                          self.auteur != suiv and (self.estPublic or suiv.is_permacat)]
                if emails:
                    try:
                        send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                    except Exception as inst:
                        mail_admins("erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))
        else:
            if sendMail:
                titre = "[Permacat-JardinPartagé] Article actualisé"
                message = "L'article '" + self.titre + "' a été modifié : http://www.perma.cat" + self.get_absolute_url() + \
                          "\n\n------------------------------------------------------------------------------" \
                          "\n vous recevez cet email, car vous avez choisi de suivre cet article sur le site http://www.Perma.Cat/jardins/articles/"

                emails = [suiv.email for suiv in followers(self) if
                          self.auteur != suiv and (self.estPublic or suiv.is_permacat)]

                if emails:
                    try:
                        send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
                    except Exception as inst:
                        mail_admins("erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))

        return super(Article, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_annonces[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

class Evenement(models.Model):
    titre = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)" )
    start_time = models.DateTimeField(verbose_name="Date", null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel pour un evenement sur plusieurs jours)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        unique_together = ('article', 'start_time',)
        db_table = 'evenement_jardin'

    def get_absolute_url(self):
        return self.article.get_absolute_url()


    @property
    def gettitre(self):
        if not self.titre:
            return self.article.titre
        return self.titre

    @property
    def estPublic(self):
        return self.article.estPublic

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_comm_jardin')
    commentaire = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_jardin')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'commentaire_jardin'

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)

    @property
    def get_edit_url(self):
        return reverse('jardinpartage:modifierCommentaireArticle',  kwargs={'id':self.id})


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
            titre = "[Permacat-JardinPartagé] article commenté"
            message = " Un article auquel vous êtes abonné a été commenté " + \
                      "\n Vous pouvez y accéder en suivant ce lien : https://permacat.herokuapp.com" + self.article.get_absolute_url() + \
                      "\n\n------------------------------------------------------------------------------" \
                      "\n vous recevez cet email, car vous avez choisi de suivre l'article (en cliquant sur la cloche) sur le site http://www.Perma.Cat/forum/articles/" + self.article.get_absolute_url()
            emails = [suiv.email for suiv in followers(self.article) if
                      self.auteur_comm != suiv and (self.article.estPublic or suiv.is_permacat)]
            try:
                send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
            except Exception as inst:
                mail_admins("erreur mails",
                            titre + "\n" + message + "\n xxx \n" + str(emails) + "\n erreur : " + str(inst))

        return super(Commentaire, self).save(*args, **kwargs)
    
class Participation(models.Model):
    participe = models.BooleanField(verbose_name="Je suis intéressé.e par les jardins partagés", default=False)
