from django.db import models
from bourseLibre.models import Profil, Suivis, Asso
from bourseLibre.constantes import Choix as Constantes
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mass_mail, mail_admins
from actstream import action
from actstream.models import followers
from bourseLibre.settings import SERVER_EMAIL, LOCALL

class Choix():
    statut_projet = ('prop','Proposition de projet'), ("AGO","Fiche projet soumise à l'AGO"), ('vote','Soumis au vote'), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),

    type_projet = ('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'), ('Projponct','Projet ponctuel'),
    type_annonce = ('Annonce','Annonce'), ('Administratif','Administratif'), ('Agenda','Agenda'),  ('Chantier','Chantier participatif'),\
                   ('Documentation','Documentation'), \
                    ('Point', 'Point de vue'),  ('Recette', 'Recette'), \
                     ('Divers','Divers'), #('Jardi','Jardi per tots'),
    type_annonce_projets = ('Altermarché', 'Altermarché'),  ('Ecovillage', 'Ecovillage'), \
                   ('Jardin', 'Jardins partagés'), #('KitPerma', 'Kit Perma Ecole'),

    couleurs_annonces = {
       # 'Annonce':"#e0f7de", 'Administratif':"#dcc0de", 'Agenda':"#d4d1de", 'Entraide':"#cebacf",
       # 'Chantier':"#d1ecdc",'Jardinage':"#fcf6bd", 'Recette':"#d0f4de", 'Bricolage':"#fff2a0",
       # 'Culture':"#ffc4c8", 'Bon_plan':"#bccacf", 'Point':"#87bfae", 'Autre':"#bcb4b4"

        'Annonce':"#d1ecdc",
        'Administratif':"#D4CF7D",
        'Agenda':"#E0E3AB",
        'Entraide':"#AFE4C1",
        'Chantier':"#fff2a0",
        'Jardi':"#B2AFE4",
        'Recette':"#d0f4de",
        'KitPerma':"#caf9b7",
        'Permaculture':"#ced2d3",
        'Bon_plan':"#349D9B",
        'Point':"#bccacf",
        'Autre':"#87bfae",
        'Ecovillage':"#cebacf",
        'Jardin':"#fffdcc",
        'Altermarché':"#daffb3",
        'Documentation':'#ddd0a8',



    }
    couleurs_projets = {
        'Part':"#d0e8da", 'AGO':"#dcc0de", 'Projlong':"#d1d0dc", 'Projcourt':"#ffc09f", 'Projponct':"#e4f9d4",
    }

    def get_couleur(categorie):
        try:
            return Choix.couleurs_annonces[categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_annonce + Choix.type_annonce_projets),
        default='Annonce', verbose_name="categorie")
    titre = models.CharField(max_length=100,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres permacat')
    estModifiable = models.BooleanField(default=False, verbose_name="Modifiable par n'importe qui")

    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, default=timezone.now)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'article")

    start_time = models.DateTimeField(verbose_name="Date de début (optionnel, affichage dans l'agenda)", null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})

    def save(self, sendMail=True, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            if sendMail:
                suivi, created = Suivis.objects.get_or_create(nom_suivi='articles')
                titre = "Nouvel article"
                message = "Un article a été posté dans le forum : '<a href='https://www.perma.cat" + self.get_absolute_url() +"'>" + self.titre + "</a>'"
                emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv and self.est_autorise(suiv)]
                if emails and not LOCALL:
                    creation = True
        else:
            if sendMail:
                titre = "Article actualisé"
                message = "L'article '<a href='https://www.perma.cat" + self.get_absolute_url() +"'>" + self.titre + "</a>' a été modifié"
                emails = [suiv.email for suiv in followers(self) if self.auteur != suiv and self.est_autorise(suiv)]

        retour =  super(Article, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_annonces[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True
        elif self.asso.abreviation == "pc":
            return user.adherent_permacat
        elif self.asso.abreviation == "ga":
            return user.adherent_ga
        elif self.asso.abreviation == "rtg":
            return user.adherent_rtg
        else:
            return False

class Evenement(models.Model):
    titre = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)" )
    start_time = models.DateTimeField(verbose_name="Date", null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel pour un evenement sur plusieurs jours)",  null=True,blank=True, help_text="jj/mm/année")


    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.start_time) + ": " + str(self.article)

    class Meta:
        unique_together = ('article', 'start_time',)

    def get_absolute_url(self):
        return self.article.get_absolute_url()


    @property
    def gettitre(self):
        if not self.titre:
            return self.article.titre
        return self.titre

    @property
    def estPublic(self):
        return self.article.asso.id == 1

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)

    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireArticle',  kwargs={'id':self.id})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles')
            titre = "Article commenté"
            message = self.auteur_comm.username + " a commenté l'article '<a href='https://www.perma.cat" + self.article.get_absolute_url() + "'>" + self.article.titre + "</a>'"
            emails = [suiv.email for suiv in followers(self.article) if
                      self.auteur_comm != suiv and self.article.est_autorise(suiv)]

        retour =  super(Commentaire, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.article.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour


    def est_autorise(self, user):
        return self.projet.est_autorise(user)

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

    start_time = models.DateTimeField(verbose_name="Date de début (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    estArchive = models.BooleanField(default=False, verbose_name="Archiver le projet")
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.slug})

    def save(self, sendMail = True, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            titre = "Nouveau Projet !"
            message = "Un nouveau projet a été proposé: '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>'"
            suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')
            emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv  and self.est_autorise(suiv)]

        else:
            if sendMail:
                titre = "Projet actualisé"
                message = "Le projet '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' a été modifié"
                emails = [suiv.email for suiv in followers(self) if
                          self.auteur != suiv and self.est_autorise(suiv)]

        retour = super(Projet, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_projets[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True
        elif self.asso.abreviation == "pc":
            return user.adherent_permacat
        elif self.asso.abreviation == "rtg":
            return user.adherent_rtg
        else:
            return False

class CommentaireProjet(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.projet)

    def get_absolute_url(self):
        return self.projet.get_absolute_url()

    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireProjet',  kwargs={'id':self.id})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            titre = "[Permacat] Projet commenté"
            message = self.auteur_comm.username + " a commenté le projet '<a href='https://www.perma.cat" + self.projet.get_absolute_url() + "'>" + self.projet.titre + "</a>'"
            emails = [suiv.email for suiv in followers(self.projet) if self.auteur_comm != suiv and self.est_autorise(suiv)]

        retour =  super(CommentaireProjet, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.projet.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour


    def est_autorise(self, user):
        return self.projet.est_autorise(user)



class EvenementAcceuil(models.Model):
    titre = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)")
    date = models.DateTimeField(verbose_name="Date", null=False, blank=False, help_text="jj/mm/année",
                                      default=timezone.now)

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.date) + ": " + str(self.article)

    class Meta:
        unique_together = ('article', 'date',)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    @property
    def gettitre(self):
        if not self.titre:
            return self.article.titre
        return self.titre
