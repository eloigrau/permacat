from django.db import models
from bourseLibre.models import Profil, Suivis, Asso, Adresse
from django.urls import reverse
from django.utils import timezone, html
from actstream import action
from actstream.models import followers
from taggit.managers import TaggableManager
from photologue.models import Album
from django.utils.text import slugify
from jardinpartage.models import Choix as Choix_jpt
from datetime import datetime, timedelta


import uuid

class Choix:
    statut_projet = ('prop','Proposition de projet'), ("AGO","Fiche projet soumise à l'AGO"), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_projet = ('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'), ('Projponct','Projet ponctuel'),
    type_annonce_base = ('Annonce','Annonce'), ('Administratif','Organisation'), ('Agenda','Agenda'),  ('Chantier','Atelier/Chantier participatif'),\
                   ('Documentation','Documentation'),  ('covoit','Covoiturage'), \
                    ('Point', 'Idée / Point de vue'),  ('Recette', 'Recette'), ('BonPlan','Bon Plan / achat groupé'), \
                     ('Divers','Divers')
    type_annonce_viure = ('Info', 'Annonce / Information'), ('Agenda', 'Agenda'), (
    'coordination', "Coordination"), ('reunion', "Réunions"), ('manifestations', 'Manifestations'),
    ('projets', 'Projets écocides')

    type_annonce_citealt_orga = ('orga1', "Cercle Organisation"), ('orga2', "Cercle Informatique"), ('orga3', "Cercle Communication"), ('orga4', "Cercle Animation"),  ('orga5', "Cercle Médiation")
    type_annonce_citealt_themes = ('theme1', "Cercle Education"), ('theme2', "Cercle Ecolieux"), ('theme3', "Cercle Santé"), ('theme4', "Cercle Echanges"),  ('theme5', "Cercle Agriculture"),  ('theme6', "Cercle Célébration")
    type_annonce_citealt_groupes = ('groupe1', "Groupe de Perpignan"), ('groupe2', "Groupe des Albères"), ('groupe3', "Groupe des Aspres"), ('groupe4', "Groupe du Vallespir"),  ('groupe5', "Groupe du Ribéral"),  ('groupe7', "Groupe du Conflent"),('groupe6', "Groupe de la côte"),
    type_annonce_citealt_groupes_logo = {'groupe1':'img/cercles/cercleBleu.png','groupe2':'img/cercles/cercleRouge.png','groupe3':'img/cercles/cercleVert.png','groupe4':'img/cercles/cercleBleuClair.png','groupe5':'img/cercles/cercleOrange.png','groupe6':'img/cercles/cercleBlanc.png','groupe7':'img/cercles/cercleJaune.png',}
    type_annonce_citealt = type_annonce_citealt_orga + type_annonce_citealt_themes + type_annonce_citealt_groupes

    type_annonce_projets = ('Altermarché', 'Altermarché'),  ('Ecovillage', 'Ecovillage'), \
                   ('Jardin', 'Jardins partagés'), ('ChantPossible', 'Ecolieu Chant des possibles'), ('BD_Fred', 'Les BD de Frédéric') , ('bzzz', 'Projet Bzzzz') #('KitPerma', 'Kit Perma Ecole'),
    type_annonce_bzz2022 =   ('AgendaBzz', 'AgendaBzz'),  ('Documentation', 'Documentation'), ('rendez-vous', 'Rendez-vous'),

    type_annonce_public = type_annonce_base + type_annonce_projets + (('professionel','Activité Pro'), ('sante','Santé et Bien-être'), )
    type_annonce_asso = {
        "public": type_annonce_public,
        "pc": type_annonce_base,
        "scic": type_annonce_base,
        "fer": type_annonce_base,
        "rtg": type_annonce_base,
        "viure": type_annonce_viure,
        "citealt": type_annonce_base + type_annonce_citealt,
        "bzz2022": type_annonce_bzz2022,
        "jp": Choix_jpt.jardins_ptg,
    }

    type_annonce = type_annonce_public + type_annonce_citealt + type_annonce_viure + type_annonce_bzz2022
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
    'orga1':'#00c40c98',
    'orga2':'#00c40c96',
    'orga3':'#00c40c94',
    'orga4':'#00c40c92',
    'orga5':'#00c40c90',
    'theme1':'#ffff0078',
    'theme2':'#ffff0076',
    'theme3':'#ffff0074',
    'theme4':'#ffff0072',
    'theme5':'#ffff0070',
    'theme6':'#ffff0068',
    'groupe1':'#ff000038',
    'groupe2':'#ff000036',
    'groupe3':'#ff000034',
    'groupe4':'#ff000032',
    'groupe5':'#ff000030',
    'groupe6':'#ff000028',


    }
    couleurs_projets = {
        'Part':"#d0e8da", 'AGO':"#dcc0de", 'Projlong':"#d1d0dc", 'Projcourt':"#ffc09f", 'Projponct':"#e4f9d4",
    }

    ordre_tri_articles = {
                             "date du dernier commentaire":'-date_dernierMessage',
                             "date de création":'-date_creation',
                             "date de la dernière modification":'-date_modification',
                             "date associée à l'article":'-start_time',
                             "titre": 'titre' }
    ordre_tri_projets = {"date de création":'-date_creation',
                         #"date du dernier commentaire":'-date_dernierMessage',
                         "Type de projet":'categorie', "statut du projet":"statut",
                         'auteur':'auteur', 'titre':'titre'}

    groupes_logo_nom = {'public': 'img/logos/nom_public.png', 'pc': 'img/logos/nom_public.png',}

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
        return 'img/logos/nom_'+abreviation+'.png'

    def get_logo_nomgroupe_html(abreviation, taille=25):
        return "<img src='/static/" + Choix.get_logo_nomgroupe(abreviation) + "' height ='"+str(taille)+"px'/>"

    def get_type_annonce_asso(asso):
        try:
            return Choix.type_annonce_asso[asso]
        except:
            return Choix.type_annonce

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices= Choix.type_annonce,
        default='', verbose_name="Dossier")
    titre = models.CharField(max_length=250,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", auto_now=False, null=True, )
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres permacat')
    estModifiable = models.BooleanField(default=False, verbose_name="Modifiable par les autres")
    estEpingle = models.BooleanField(default=False, verbose_name="Article épinglé")

    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, null=True, blank=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'article")

    start_time = models.DateField(verbose_name="Date de l'événement (pour apparaitre sur l'agenda, sinon vous pourrez ajouter des évènements depuis l'article) ", null=True, blank=True, help_text="jj/mm/année")
    end_time = models.DateField(verbose_name="Date de fin (optionnel, pour affichage dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    tags = TaggableManager(verbose_name="Mots clés",  help_text="Liste de mots-clés séparés par une virgule", blank=True)

    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Album photo associé",  )

    partagesAsso = models.ManyToManyField(Asso, related_name="asso_partages", verbose_name="Partagé avec :", blank=True)

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})


    def sendMailArticle_newormodif(self, creation, forcerCreationMails):
        emails = []
        if creation or forcerCreationMails:
            titre = "Nouvel article"
            message = "Un article a été posté dans le forum [" + str(
                self.asso.nom) + "] : '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>'"
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(self.asso.abreviation))
            emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv and self.est_autorise(suiv)]
            for asso in self.partagesAsso.all():
                suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(asso.abreviation))
                emails += [suiv.email for suiv in followers(suivi) if self.auteur != suiv and self.est_autorise(suiv)]
        else:
            temps_depuiscreation = timezone.now() - self.date_creation
            if temps_depuiscreation > timedelta(minutes=10):
                titre = "Article actualisé"
                message = "L'article [" + str(self.asso.nom) + "] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' a été modifié"
                emails = [suiv.email for suiv in followers(self) if self.est_autorise(suiv)]

        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)


    def save(self, sendMail=True, saveModif=True, forcerCreationMails=False, *args, **kwargs):
        ''' On save, update timestamps '''
        sendMail = sendMail and getattr(self, "sendMail", True)
        creation = False
        if not self.id:
            creation = True
            self.date_creation = timezone.now()
        else:
            if saveModif:
                self.date_modification = timezone.now()

        retour = super(Article, self).save(*args, **kwargs)

        if creation:
            discussion, created = Discussion.objects.get_or_create(article=self, titre="Discussion Générale")

        if sendMail:
            self.sendMailArticle_newormodif(creation, forcerCreationMails)

        return retour

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_annonces[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

    @property
    def get_partagesAsso(self):
        x = self.partagesAsso.filter(abreviation='public')
        if x:
            return x
        return self.partagesAsso.exclude(abreviation=self.asso.abreviation)

    @property
    def get_partagesAssotxt(self):
        return "\n".join([str(p) for p in self.get_partagesAsso])#"\n".join(

    @property
    def get_partagesAssoLogo(self):
        return html.format_html("{}", html.mark_safe(" ".join([Choix.get_logo_nomgroupe_html(p.abreviation, taille=20) for p in self.get_partagesAsso])))

    @property
    def get_logo_categorie(self):
        return Choix.get_logo(self.categorie)

    @property
    def get_logo_nomgroupe(self):
        return Choix.get_logo_nomgroupe(self.asso.abreviation)

    @property
    def get_logo_nomgroupe_html(self):
        return self.get_logo_nomgroupe_html_taille(25)

    def get_logo_nomgroupe_html_taille(self, taille=25):
        return Choix.get_logo_nomgroupe_html(self.asso.abreviation, taille)#"<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

    @property
    def get_logo_nomgroupespartages_html(self):
        return self.get_logo_nomgroupes_partages_html_taille(15)

    def get_logo_nomgroupes_partages_html_taille(self, taille=15):
        return [Choix.get_logo_nomgroupe_html(asso.abreviation, taille) for asso in self.get_partagesAsso]#"<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

    def est_autorise(self, user):
        if self.asso.abreviation == "public" or self.partagesAsso.filter(abreviation="public"):
            return True
        adhesion = getattr(user, "adherent_" + self.asso.abreviation)
        if adhesion :
            return adhesion
        for asso in self.get_partagesAsso:
            if getattr(user, "adherent_" + asso.abreviation):
                return True
        return False

    def getLieux(self):
        return AdresseArticle.objects.filter(article=self)

    @property
    def derniereDate(self):
        derniere_date = self.date_modification if self.date_modification else self.date_creation
        if self.date_dernierMessage and self.date_dernierMessage > derniere_date:
            return self.date_dernierMessage
        else:
            return derniere_date


class Evenement(models.Model):
    titre_even = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article" )
    start_time = models.DateField(verbose_name="Date", null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateField(verbose_name="Date de fin (optionnel pour un evenement sur plusieurs jours)",  null=True,blank=True, help_text="jj/mm/année")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)

    def __str__(self):
        return "(" + str(self.titre) + ") "+ str(self.start_time) + ": " + str(self.article)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    @property
    def slug(self):
        return self.article.slug

    @property
    def titre(self):
        if not self.titre_even:
            return self.article.titre
        return self.titre_even

    @property
    def estPublic(self):
        return self.article.asso.id == 1

    def est_autorise(self, user):
        return self.article.est_autorise(user)

    @property
    def get_logo_categorie(self):
        return self.article.get_logo_categorie

    @property
    def get_logo_nomgroupe(self):
        return self.article.get_logo_nomgroupe

class Discussion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    titre = models.CharField(blank=False, max_length=32, verbose_name="Titre de la discussion")
    slug = models.SlugField(max_length=32, default=uuid.uuid4)

    class Meta:
        unique_together = ('article', 'slug',)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.titre) + " (" + str(self.article) + ")"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)
        super(Discussion, self).save(*args, **kwargs)

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)

    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireArticle',  kwargs={'id':self.id})

    def save(self, sendMail=False, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(self.article.asso.abreviation))
            titre = "Article commenté"
            message = str(self.auteur_comm.username) + " a commenté l'article [" + str(self.article.asso.nom) + "] '<a href='https://www.perma.cat" + str(self.article.get_absolute_url()) + "'>" + str(self.article.titre) + "</a>'"
            emails = [suiv.email for suiv in followers(self.article) if
                      self.auteur_comm != suiv and self.article.est_autorise(suiv)]

            self.article.date_dernierMessage = timezone.now()
            self.article.save(sendMail)

        retour = super(Commentaire, self).save(*args, **kwargs)
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
    titre = models.CharField(max_length=250)
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

    date_dernierMessage = models.DateTimeField(verbose_name="Date de Modification", auto_now=False, blank=True, null=True)
    dernierMessage = models.CharField(max_length=100, default="", blank=True, null=True)

    start_time = models.DateField(verbose_name="Date de début (optionnel, pour apparaitre dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateField(verbose_name="Date de fin (optionnel, pour apparaitre dans l'agenda)",  null=True,blank=True, help_text="jj/mm/année")

    estArchive = models.BooleanField(default=False, verbose_name="Archiver le projet")
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    tags = TaggableManager(verbose_name="Mots clés", help_text="Liste de mots-clés séparés par une virgule", blank=True)

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
            message = "Un nouveau projet a été proposé: ["+ self.asso.nom +"] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + str(self.titre) + "</a>'"
            suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')
            emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv  and self.est_autorise(suiv)]

        else:
            if sendMail:
                titre = "Projet actualisé"
                message = "Le projet ["+ self.asso.nom +"] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + str(self.titre) + "</a>' a été modifié"
                emails = [suiv.email for suiv in followers(self) if
                          self.auteur != suiv and self.est_autorise(suiv)]

        retour = super(Projet, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_projets[str(self.categorie)]
        except:
            return Choix.couleurs_annonces["Autre"]

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True

        return getattr(user, "adherent_" + self.asso.abreviation)

    @property
    def has_ficheprojet(self):
        return hasattr(self, "ficheprojet")

class FicheProjet(models.Model):
    projet = models.OneToOneField(Projet, on_delete=models.CASCADE, primary_key=True,)
    date_creation = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    date_modification = models.DateTimeField(verbose_name="Date de modification", auto_now=True)
    raison = models.TextField(null=True, blank=True, verbose_name="Raison d'Etre du projet")
    pourquoi_contexte = models.TextField(null=True, blank=True, verbose_name="Pourquoi ? Le contexte")
    pourquoi_motivation = models.TextField(null=True, blank=True, verbose_name="Pourquoi ? Les motivations")
    pourquoi_objectifs = models.TextField(null=True, blank=True, verbose_name="Pourquoi ? Les objectifs")
    pour_qui = models.TextField(null=True, blank=True, verbose_name="Pour qui ? Le public")
    par_qui = models.TextField(null=True, blank=True, verbose_name="Par qui ? Les acteurs")
    avec_qui = models.TextField(null=True, blank=True, verbose_name="Par qui ? Les partenaires")
    ou = models.TextField(null=True, blank=True, verbose_name="Où ?")
    quand = models.TextField(null=True, blank=True, verbose_name="Début ? La périodicité")
    comment = models.TextField(null=True, blank=True, verbose_name="Comment ? La méthodologie")
    combien = models.TextField(null=True, blank=True, verbose_name="Combien ? Le budget prévisionnel")

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return "Fiche du projet" + str(self.projet) + " créée le " + str(self.date_creation) + " "+ str(self.raison)

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.projet.slug})

    def est_autorise(self, user):
        if self.projet.asso.abreviation == "public":
            return True

        return getattr(user, "adherent_" + self.projet.asso.abreviation)


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
            self.projet.date_dernierMessage = timezone.now()
            self.projet.save()
            message = self.auteur_comm.username + " a commenté le projet '<a href='https://www.perma.cat" + self.projet.get_absolute_url() + "'>" + self.projet.titre + "</a>'"
            emails = [suiv.email for suiv in followers(self.projet) if self.auteur_comm != suiv and self.est_autorise(suiv)]

        retour =  super(CommentaireProjet, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.projet.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour


    def est_autorise(self, user):
        return self.projet.est_autorise(user)



class EvenementAcceuil(models.Model):
    titre_even = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)")
    date = models.DateTimeField(verbose_name="Date", null=False, blank=False, help_text="jj/mm/année",
                                      default=timezone.now)

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.date) + ": " + str(self.article)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    @property
    def titre(self):
        if not self.titre_even:
            return self.article.titre
        return self.titre_even

    def est_autorise(self, user):
        return self.article.est_autorise(user)

class AdresseArticle(models.Model):
    titre = models.CharField(verbose_name="Nom du lieu",
                             max_length=100, null=True, blank=True, default="")
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE,)
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)")


    def __str__(self):
        if self.titre:
            return str(self.titre) + " : " + str(self.adresse.get_adresse_str)
        else:
            return str(self.adresse.get_adresse_str)


    @property
    def get_titre(self):
        if not self.titre:
            return ""
        return self.titre