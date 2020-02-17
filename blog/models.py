from django.db import models
from bourseLibre.models import Profil, Suivis
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mass_mail
#from tinymce.models import HTMLField
from django.dispatch import receiver
from django.db.models.signals import post_save

from actstream.models import followers

class Choix():
    statut_projet = ('prop','Proposition de projet'), ("AGO","Fiche prpojet soumise à l'AGO"), ('vote','Soumis au vote'), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_projet = ('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'), ('Projponct','Projet ponctuel'),
    type_annonce = ('Altermarché','Altermarché'), ('Annonce','Annonce'), ('Administratif','Administratif'), ('Agenda','Agenda'), ('Bricolage','Bricolage'), ('Chantier','Chantier participatif'),\
                   ('Documentation','Documentation'),('Ecovillage', 'Ecovillage'),  ('Entraide','Entraide'), \
                    ('Permaculture','Permaculture'),  ('Point', 'Point de vue'), \
                     ('Projet', 'Projet'),   ('Recette', 'Recette'), \
                    ('Serre','Serre collective'),('Autre','Autre'),
    couleurs_annonces = {
       # 'Annonce':"#e0f7de", 'Administratif':"#dcc0de", 'Agenda':"#d4d1de", 'Entraide':"#cebacf",
       # 'Chantier':"#d1ecdc",'Jardinage':"#fcf6bd", 'Recette':"#d0f4de", 'Bricolage':"#fff2a0",
       # 'Culture':"#ffc4c8", 'Bon_plan':"#bccacf", 'Point':"#87bfae", 'Autre':"#bcb4b4"

        'Annonce':"#d1ecdc",
        'Administratif':"#D4CF7D",
        'Agenda':"#E0E3AB",
        'Entraide':"#AFE4C1",
        'Chantier':"#fff2a0",
        'Jardinage':"#B2AFE4",
        'Recette':"#d0f4de",
        'Bricolage':"#6E74CF",
        'Culture':"#3EA7BB",
        'Bon_plan':"#349D9B",
        'Point':"#bccacf",
        'Autre':"#87bfae",
        'Ecovillage':"#cebacf",
        'Serre':"#fffdcc",
        'Altermarché':"#daffb3",
        #664D00



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
        choices=(Choix.type_annonce),
        default='Annonce', verbose_name="categorie")
    titre = models.CharField(max_length=100,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
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
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()
        return super(Article, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_annonces[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]


@receiver(post_save, sender=Article)
def on_save_articles(instance, created, **kwargs):
    if created:
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles')
        titre = "Permacat - nouvel article"
        message = " Un nouvel article a été créé " + \
                  "\n Vous pouvez y accéder en suivant ce lien : https://permacat.herokuapp.com" + instance.get_absolute_url() + \
                  "\n\n------------------------------------------------------------------------------" \
                  "\n vous recevez cet email, car vous avez choisi de suivre les articles (en cliquant sur la cloche) sur le site http://www.Perma.Cat/forum/articles/"
        emails = [suiv.email for suiv in followers(suivi) if instance.auteur != suiv and (instance.estPublic or suiv.is_permacat)]
        try:
            send_mass_mail([(titre, message, "asso@perma.cat", emails), ])
        except:
            pass


class Evenement(models.Model):
    titre = models.CharField(verbose_name="Titre de l'événement (si laissé vide, ce sera le titre de l'article)",
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)" )
    start_time = models.DateTimeField(verbose_name="Date", null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateTimeField(verbose_name="Date de fin (optionnel pour un evenement sur plusieurs jours)",  null=True,blank=True, help_text="jj/mm/année")

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
        return self.article.estPublic

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

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.date_creation = timezone.now()

        return super(Projet, self).save(*args, **kwargs)

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_projets[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

@receiver(post_save,  sender=Projet)
def on_save_projet(instance, **kwargs):
    titre = "Permacat - Projet  actualisé"
    message = " Le projet '" +  instance.titre + "' a été modifié (ou quelqu'un l'a commenté)"+ \
              "\n Vous pouvez y accéder en suivant ce lien : https://permacat.herokuapp.com" + instance.get_absolute_url() + \
              "\n\n------------------------------------------------------------------------------" \
              "\n vous recevez cet email, car vous avez choisi de suivre cet article sur le site http://www.Perma.Cat/forum/projets/"
    emails = [suiv.email for suiv in followers(instance)  if instance.auteur != suiv  and (instance.estPublic or suiv.is_permacat)]
    try:
        send_mass_mail([(titre, message, "asso@perma.cat", emails), ])
    except:
        pass


@receiver(post_save, sender=Projet)
def on_save_projets(instance, created, **kwargs):
    if created:
        suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')
        titre = "Permacat - nouveau Projet"
        message = " Un nouveau projet a été créé !" + \
                  "\n Vous pouvez y accéder en suivant ce lien : https://permacat.herokuapp.com" + instance.get_absolute_url() +\
                  "\n\n------------------------------------------------------------------------------" \
                  "\n vous recevez cet email, car vous avez choisi de suivre les projets (en cliquant sur la cloche)  sur le site http://www.Perma.Cat/forum/projets/"
        emails = [suiv.email for suiv in followers(suivi) if instance.auteur != suiv and (instance.estPublic or suiv.is_permacat)]
        try:
            send_mass_mail([(titre, message, "asso@perma.cat", emails), ])
        except:
            pass


@receiver(post_save,  sender=Article)
def on_save_article(instance, **kwargs):
    titre = "Permacat - Article actualisé"
    message = "L'article '" +  instance.titre + "' a été modifié (ou quelqu'un l'a commenté)" +\
              "\n Vous pouvez y accéder en suivant ce lien : http://www.perma.cat" + instance.get_absolute_url() + \
              "\n\n------------------------------------------------------------------------------" \
              "\n vous recevez cet email, car vous avez choisi de suivre ce projet sur le site http://www.Perma.Cat/forum/articles/"
   # emails = [(titre, message, "asso@perma.cat", (suiv.email, )) for suiv in followers(instance)]
    emails = [suiv.email for suiv in followers(instance)  if instance.auteur != suiv  and (instance.estPublic or suiv.is_permacat)]
    try:
        send_mass_mail([(titre, message, "asso@perma.cat", emails), ])
    except:
        pass



class CommentaireProjet(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.projet)


    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireProjet',  kwargs={'id':self.id})