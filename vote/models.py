from django.db import models
from bourseLibre.models import Profil, Asso
from django.urls import reverse
from django.utils import timezone
from actstream.models import followers
from bourseLibre.models import Suivis
from actstream import action

class Choix():
    vote_ouinon = (('', '-----------'),
                     ('0', ("Oui")),
                    ('1', ("Non")),
                    ('2', ("Ne se prononce pas")))

    type_vote = (('', '-----------'),
                     ('0', ("Vote d'un projet")),
                    ('1', ("Vote d'une décision")),
                    ('2', ("Sondage")))

    couleurs_annonces = {
            '0':"#d1ecdc",
            'Coordination':"#D4CF7D",
            '1':"#E0E3AB",
            'Potager':"#AFE4C1",
            'PPAM':"#fff2a0",
            'Arbres':"#B2AFE4",
            'Administratif':"#d0f4de",
            '2':"#caf9b7",
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

class Suffrage(models.Model):
    type_vote = models.CharField(max_length=30,
        choices=(Choix.type_vote), default='', verbose_name="Type de vote")
    question = models.CharField(max_length=100, verbose_name="Question soumise au vote ?")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_suffrage')
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True, verbose_name="Description du contexte")
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    estPublic = models.BooleanField(default=False, verbose_name='Public ou réservé aux membres permacat')
    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=True)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver la proposition")
    estAnonyme = models.BooleanField(default=False, verbose_name="Vote anonyme")

    start_time = models.DateTimeField(verbose_name="Date de début", null=True,blank=False, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin",  null=True,blank=False, help_text="jj/mm/année")
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ('-date_creation', )
        db_table = 'suffrage'

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('vote:lireSuffrage', kwargs={'slug':self.slug})

    def save(self, userProfile=None, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            suivi, created = Suivis.objects.get_or_create(nom_suivi='suffrages')
            titre = "Nouveau vote"
            message = userProfile.username + " a lancé un nouveau vote: '<a href='https://www.perma.cat"+ self.get_absolute_url() + "'>"+ self.question + "</a>'"
            emails = [suiv.email for suiv in followers(suivi) if userProfile != suiv and self.est_autorise(suiv)]

        retour = super(Suffrage, self).save(*args, **kwargs)

        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

    def getResultats(self):
        votes = Vote.objects.filter(suffrage=self)
        votesOui = votes.filter(choix='0')
        votesNon = votes.filter(choix='1')
        votesNSPP = votes.filter(choix='2')
        nbOui = len(votesOui)
        nbNon = len(votesNon)
        nbNSPP = len(votesNSPP)
        nbTotal = nbOui + nbNon + nbNSPP
        if nbTotal > 0:
            nbOui = (len(votesOui), str(round(len(votesOui) * 100 / nbTotal, 1)) + '%')
            nbNon = (len(votesNon), str(round(len(votesNon) * 100 / nbTotal, 1)) + '%')
            nbNSPP = (len(votesNSPP), str(round(len(votesNSPP) * 100 / nbTotal, 1)) + '%')
            if nbOui > nbNon:
                resultat = 'Oui à ' + str(round(nbOui[0] * 100 / nbTotal, 1)) + ' %'
            elif nbNon > nbOui:
                resultat = 'Non à ' + str(round(nbNon[0] * 100 / nbTotal, 1)) + ' %'
            else:
                resultat = 'Ex aequo à ' + str(round(nbOui[0] * 100 / nbTotal, 1)) + ' %'
        else:
            nbOui = (0, '0%')
            nbNon = (0, '0%')
            nbNSPP = (0, '0%')
            resultat = "pas de votants"
        return {'nbOui':nbOui, 'nbNon':nbNon, 'nbNSPP':nbNSPP, 'nbTotal':nbTotal, 'resultat':resultat, 'votes':votes}

    @property
    def getResultat(self):
        statut = self.get_statut
        if  statut[0] != 1:
            return statut[1]
        return self.getResultats()['resultat']

    @property
    def get_statut(self):
        if self.start_time < timezone.now():
            if self.end_time > timezone.now():
                statut = (0, "Le vote est en cours ")
            else:
                statut = (1, "Le vote est terminé ")
        else:
            statut = (2, "Le vote n'a pas encore démarré ")
        return statut

    @property
    def get_couleur(self):
        return Choix.get_couleur(self.type_vote)

    def est_autorise(self, user):
        if self.asso.abreviation == "public":
            return True
        elif self.asso.abreviation == "pc":
            return user.adherent_permacat
        elif self.asso.abreviation == "rtg":
            return user.adherent_rtg
        elif self.asso.abreviation == "fer":
            return user.adherent_fer
        else:
            return False

class Vote(models.Model):
    choix = models.CharField(max_length=30,
        choices=(Choix.vote_ouinon),
        default='', verbose_name="Choix du vote :")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_vote', null=True)
    suffrage = models.ForeignKey(Suffrage, on_delete=models.CASCADE, related_name='suffrage')
    date_creation = models.DateTimeField(verbose_name="Date de parution", auto_now_add=True)
    date_modification = models.DateTimeField(verbose_name="Date de modification", auto_now=True)
    commentaire = models.TextField(verbose_name="Commentaire", null=True, blank=True)

    def __str__(self):
        return str(self.suffrage) + " " + dict(Choix.vote_ouinon)[self.choix]

    def getVoteStr(self):
        return dict(Choix.vote_ouinon)[self.choix]

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_comm_vote')
    commentaire = models.TextField()
    suffrage = models.ForeignKey(Suffrage, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.auteur_comm) + ": " + str(self.suffrage)

    @property
    def get_edit_url(self):
        return reverse('vote:modifierCommentaireSuffrage', kwargs={'id': self.id})

    def get_absolute_url(self):
        return self.suffrage.get_absolute_url()
