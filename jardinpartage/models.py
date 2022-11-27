from django.db import models
from bourseLibre.models import Profil, Suivis
from django.urls import reverse
from django.utils import timezone
#from django.core.mail import send_mass_mail, mail_admins
from actstream import action


from actstream.models import followers
#from bourseLibre.settings import SERVER_EMAIL, LOCALL

class Choix():
    type_annonce = ('Discu','Information'), ('Organisation', 'Organisation'), \
                  ('Potager','Au potager'), ('PPAM','PPAM'), ('Arbres','Les arbres au jardin'), \
                  ('Agenda','Agenda'), ("todo", "A faire"), \
                   ('Documentation','Documentation'),  \
                 ('Autre','Autre'),
    jardins_ptg = ('0', 'Tous les jardins'),('1', 'Jardi Per Tots'), ('2', 'Jardin de Palau'), ('3', 'Jardins de Lurçat'), ('4', 'Gardiens de la Terre'), ('5', 'Fermille'), ('6', 'Chez Claire')
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

    def get_logo(categorie):
        try:
            return Choix.type_annonce_citealt_groupes_logo[categorie]
        except:
            return ""

    def get_logo_nomgroupe(abreviation):
        return 'img/logos/nom_jpt.png'

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices=(Choix.type_annonce),
        default='Discu', verbose_name="categorie")
    jardin = models.CharField(max_length=30,
        choices=(Choix.jardins_ptg),
        default='0', verbose_name="Jardin")
    titre = models.CharField(max_length=100,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_article_jardin')
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres permacat')
    estModifiable = models.BooleanField(default=False, verbose_name="Modifiable par les autres")

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'article")

    start_time = models.DateField(verbose_name="Date de l'évenement (pour affichage dans l'agenda) - date de début si l'événement a lieu sur plusieurs jours ", null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        ordering = ('-date_creation', )
        db_table = 'article_jardin'

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('jardinpartage:lireArticle', kwargs={'slug':self.slug})


    def save(self, sendMail=True, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            if sendMail:
                suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_jardin')
                titre = "Nouvel article Jardins"
                message = "Nouvel article aux Jardins Partagés: '<a href='https://www.perma.cat" + self.get_absolute_url() +"'>" + self.titre + "</a>'"
                emails = [suiv.email for suiv in followers(suivi) if
                          self.auteur != suiv and self.est_autorise(suiv)]
        else:
            if sendMail:
                titre = "Article actualisé Jardins"
                message = "L'article '<a href='https://www.perma.cat" + self.get_absolute_url() +"'>" + self.titre + "</a>' des Jardins Partagés a été modifié "
                emails = [suiv.email for suiv in followers(self) if self.est_autorise(suiv)]

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
        return True

    @property
    def estPublic(self):
        return True

    @property
    def get_jardin_num(self):
        return self.jardin#[item[0] for item in Choix.jardins_ptg if item[1] == self.jardin]

    @property
    def get_logo_categorie(self):
        return Choix.get_logo(self.categorie)

    @property
    def get_logo_nomgroupe(self):
        return Choix.get_logo_nomgroupe(self.jardin)

    @property
    def get_logo_nomgroupe_html(self):
        return self.get_logo_nomgroupe_html_taille()

    def get_logo_nomgroupe_html_taille(self, taille=30):
        return "<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

class Evenement(models.Model):
    titre_even = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article" )
    start_time = models.DateField(verbose_name="Date", null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateField(verbose_name="Date de fin (optionnel pour un evenement sur plusieurs jours)",  null=True,blank=True, help_text="jj/mm/année")

    class Meta:
        unique_together = ('article', 'start_time',)
        db_table = 'evenement_jardin'

    def get_absolute_url(self):
        return self.article.get_absolute_url()


    @property
    def titre(self):
        if not self.titre_even:
            return self.article.titre
        return self.titre_even

    @property
    def estPublic(self):
        return True

    def est_autorise(self, user):
        return self.article.est_autorise(user)

    @property
    def get_logo_categorie(self):
        return self.article.get_logo_categorie

    @property
    def get_logo_nomgroupe(self):
        return self.article.get_logo_nomgroupe

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_comm_jardin')
    commentaire = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_jardin')
    date_creation = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    class Meta:
        db_table = 'commentaire_jardin'

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)

    @property
    def get_edit_url(self):
        return reverse('jardinpartage:modifierCommentaireArticle',  kwargs={'id':self.id})

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            titre = "article jardins commenté "
            message = self.auteur_comm.username + " a commenté l'article [Jardins Partagés] '<a href='https://www.perma.cat"+ self.article.get_absolute_url() + "'>"+ self.article.titre + "</a>'"
            emails = [suiv.email for suiv in followers(self.article) if self.auteur_comm != suiv and self.article.est_autorise(suiv)]

        retour =  super(Commentaire, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.article.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

    def est_autorise(self, user):
        return self.article.est_autorise(user)

class Participation(models.Model):
    participe = models.BooleanField(verbose_name="Je suis intéressé.e par les jardins partagés", default=False)
