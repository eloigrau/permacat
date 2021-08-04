import itertools

from django.db import models
from bourseLibre.models import Profil, Asso
from django.urls import reverse
from django.utils import timezone
from actstream.models import followers
from bourseLibre.models import Suivis
from actstream import action
from functools import cmp_to_key
from django.core.validators import MinLengthValidator

class Choix():
    vote_ouinon = (('', '-----------'),
                     ('0', ("Oui")),
                    ('1', ("Non")),
                    ('2', ("Ne se prononce pas")))
    vote_majoritaire = (('', '-----------'),
                     ('0', ("pas du tout d'accord")),
                    ('1', ("Plutot pas d'accord")),
                    ('2', ("Neutre")),
                    ('3', ("Plutot d'accord")),
                    ('4', ("Tout à fait d'accord")))

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


def sort_candidats(a, b):
    """
    Sort candidates by their majority gauge.

    a & b are the majority gauges of the candidates A & B
    (p_A, α_A, q_A) & (p_B, α_B, q_B)
    where
    - α is the majority grade;
    - p the percentage of votes strictly above α;
    - q the percentage of votes strictly below α.
    thus, A > B ⇔ α_A > α_B || (α_A == α_B && (p_A > max(q_A, p_B, q_B) || q_B > max(p_A, q_A, p_B)))
    (eq. 2, p.11 of the second article in README.md)
    """
    a, b = a.majority_gauge(), b.majority_gauge()
    if a[1] > b[1]:
        return 1
    if b[1] > a[1]:
        return -1
    if a[0] > max(a[2], b[0], b[2]):
        return 1
    if b[0] > max(b[2], a[0], a[2]):
        return -1
    if b[2] > max(a[0], a[2], b[0]):
        return 1
    if a[2] > max(b[0], b[2], a[0]):
        return -1
    return 0


class SuffrageBase(models.Model):
    type_vote = models.CharField(max_length=30,
        choices=(Choix.type_vote), default='', verbose_name="Type de vote")
    titre = models.CharField(max_length=100, verbose_name="Titre du sondage")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_suffrage')
    slug = models.SlugField(max_length=100)
    description = models.TextField(null=True, verbose_name="Description du contexte")
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, blank=True, null=True)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)
    estArchive = models.BooleanField(default=False, verbose_name="Archiver la proposition")
    estAnonyme = models.BooleanField(default=False, verbose_name="Vote anonyme")

    start_time = models.DateTimeField(verbose_name="Date de début", null=True,blank=False, help_text="jj/mm/année")
    end_time = models.DateTimeField(verbose_name="Date de fin",  null=True,blank=False, help_text="jj/mm/année")
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True



class Suffrage(SuffrageBase):
    class Meta:
        ordering = ('-date_creation', )
        db_table = 'suffrage'

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('vote:lireSuffrage', kwargs={'slug':self.slug})

    def save(self, userProfile=None, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            suivi, created = Suivis.objects.get_or_create(nom_suivi='suffrages')
            titre = "Nouveau vote"
            message = userProfile.username + " a lancé un nouveau vote: '<a href='https://www.perma.cat"+ self.get_absolute_url() + "'>"+ self.titre + "</a>'"
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
        if statut[0] != 1:
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

        return getattr(user, "adherent_" + self.asso.abreviation)


    def get_questions(self):
        questions_b = Question_binaire.objects.filter(suffrage=self)
        questions_m = Question_majoritaire.objects.filter(suffrage=self)
        return questions_b, questions_m

    def get_propositions(self):
        return Proposition_m.objects.filter(question__suffrage=self)


class Question_base(models.Model):
    suffrage = models.ForeignKey(Suffrage, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return reverse('vote:lireSuffrage', kwargs={'slug':self.suffrage.slug})

    def __str__(self):
        if getattr(self, "question"):
            question = self.question

            if self.question and self.question[-1] != "?":
                question += "?"

            return question
        return ""

    def clean(self):
        from django.core.exceptions import ValidationError
        if getattr(self, "question") and self.question == '':
            raise ValidationError('Empty error message')

class Question_binaire(Question_base):
    question = models.CharField(max_length=100, verbose_name="Question (oui/non) soumise au vote ?", validators=[MinLengthValidator(1)])

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


class Question_majoritaire(Question_base):
    question = models.CharField(max_length=100, verbose_name="Question (jugement majoritaire) soumise au vote ?",  validators=[MinLengthValidator(1)])

    def results(self):
        """Get the sorted list of all Candidates for this Election."""
        return sorted(self.proposition_m_set.all(), key=cmp_to_key(sort_candidats))

    @property
    def propositions(self):
        return self.proposition_m_set.all()

class Proposition_m(models.Model):
    """An Election as Proposition_m as choices."""
    question = models.ForeignKey(Question_majoritaire, on_delete=models.CASCADE)
    proposition = models.CharField(max_length=500, verbose_name="Proposition", null=False, blank=False, )

    def __str__(self):
        """Print the candidate."""
        return str(self.proposition)

    def get_absolute_url(self):
        """Get the candidate's Election URL."""
        return self.question.get_absolute_url()

    def majority_gauge(self):
        """Compute the majority gauge of this Candidate."""
        count = self.vote_set.count()
        if not count:
            return (0, 10, 0)
        mention = self.vote_set.order_by('choice')[count // 2].choice
        if mention is None:
            print(self.vote_set.order_by('choice'))
            mention = 6
        return (self.vote_set.filter(choice__gt=mention).count() / count, mention,
                self.vote_set.filter(choice__lt=mention).count() / count)

    def votes(self):
        """Get the list of the votes for this Candidate."""
        count = self.vote_set.count()
        if count:
            return [self.vote_set.filter(choice=i).count() * 100 / count for i in [x[0] for x in Choix.vote_majoritaire]]
        return [0] * len(Choix.vote_majoritaire)



class Vote(models.Model):
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_vote')
    suffrage = models.ForeignKey(Suffrage, on_delete=models.CASCADE, related_name='suffrage')
    date_creation = models.DateTimeField(verbose_name="Date de parution", auto_now_add=True)
    date_modification = models.DateTimeField(verbose_name="Date de modification", auto_now=True)
    commentaire = models.TextField(verbose_name="Commentaire", null=True, blank=False)

    class Meta:
        unique_together = ('auteur', 'suffrage')

    def __str__(self):
        return str(self.suffrage) + "vote " + str(self.auteur)

    def getVoteStr(self):
        rep_b = ReponseQuestion_b.objects.filter(vote=self)
        rep_m = ReponseQuestion_m.objects.filter(vote=self)
        return [str(x) for x in itertools.chain(rep_b, rep_m)]

class ReponseQuestion_b(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='rep_question_b')
    question = models.ForeignKey(Question_binaire, on_delete=models.DO_NOTHING,)
    choix = models.CharField(max_length=30,
        choices=(Choix.vote_ouinon),
        default='', verbose_name="Choix du vote :")

    def __str__(self):
        return str(self.choix)

class ReponseQuestion_m(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='rep_question_m')
    proposition = models.ForeignKey(Proposition_m, on_delete=models.CASCADE,)
    choix = models.CharField(max_length=30,
        choices=(Choix.vote_majoritaire),
        default='', verbose_name="Choix du vote :")

    def __str__(self):
        return str(self.choix)

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
