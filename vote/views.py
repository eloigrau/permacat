# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.utils.html import strip_tags
from .models import Suffrage, Commentaire, Choix, Vote, Proposition_m, Question_binaire, Question_majoritaire
from bourseLibre.constantes import Choix as Choix_global
from .forms import SuffrageForm, CommentaireSuffrageForm, CommentaireSuffrageChangeForm, SuffrageChangeForm, \
    VoteForm, VoteChangeForm, Question_majoritaire_Form, Question_binaire_formset, Proposition_m_formset, Reponse_binaire_Form, Reponse_majoritaire_Form
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.utils.timezone import now
from django.db.models import Q
from actstream import actions, action
from actstream.models import followers, following, action_object_stream
from bourseLibre.models import Suivis, Profil, Asso
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotAllowed
from django.forms import formset_factory
import itertools
from bourseLibre.views_base import DeleteAccess
from blog.models import Article

def accueil(request):
    return render(request, 'vote/accueil.html')


@login_required
def ajouterSuffrage(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    form = SuffrageForm(request.POST or None)
    #qb_formset = Question_binaire_formset(request.POST or None, prefix="qb")
    #qm_formset = Question_majoritaire_formset(request.POST or None, prefix="qm")
    if form.is_valid() :#and qb_formset.is_valid() and qm_formset.is_valid() :
        suffrage = form.save(request.user, article)
        #for form in itertools.chain(qb_formset, qm_formset): # meme question
            # extract name from each form and save
        #    form.save(suffrage=suffrage)

        if suffrage:
            url = suffrage.get_absolute_url()
            suffix = "_" + suffrage.asso.abreviation
            action.send(request.user, verb='suffrage_ajout'+suffix, action_object=suffrage, url=url,
                        description="a ajouté un suffrage : '%s'" % suffrage.titre)

            return render(request, 'vote/ajouterQuestions.html', {'suffrage':suffrage})

    return render(request, 'vote/ajouterSuffrage.html', { "form": form, }) #"qb_formset":qb_formset, "qm_formset":qm_formset })


@login_required
def ajouterQuestion(request, slug):
    suffrage = Suffrage.objects.get(slug=slug)
    return render(request, 'vote/ajouterQuestions.html', {'suffrage':suffrage})

@login_required
def ajouterQuestionB(request, slug):
    suffrage = Suffrage.objects.get(slug=slug)
    qb_formset = Question_binaire_formset(request.POST or None, prefix="qb")
    if qb_formset.is_valid():
        for form in qb_formset: # meme question
            # extract name from each form and save
            form.save(suffrage=suffrage)

        return render(request, 'vote/ajouterQuestions.html', {'suffrage':suffrage})

    return render(request, 'vote/ajouterQuestionB.html', { "suffrage": suffrage, "qb_formset":qb_formset})

@login_required
def supprimerQuestionB(request, slug, id_question):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    if suffrage.auteur != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")
    question = Question_binaire.objects.get(suffrage=suffrage, id=id_question)
    question.delete()
    return redirect(suffrage.get_modifQuestions_url())

@login_required
def supprimerQuestionM(request, slug, id_question):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    if suffrage.auteur != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")
    question = Question_majoritaire.objects.get(suffrage=suffrage, id=id_question)
    question.delete()
    return redirect(suffrage.get_modifQuestions_url())

@login_required
def supprimerPropositionM(request, slug, id_question, id_proposition):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    if suffrage.auteur != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")
    proposition = Proposition_m.objects.get(question_m__id=id_question, id=id_proposition)
    proposition.delete()
    return redirect(suffrage.get_modifQuestions_url())

@login_required
def ajouterQuestionM(request, slug):
    suffrage = Suffrage.objects.get(slug=slug)

    form = Question_majoritaire_Form(request.POST or None)
    pm_formset = Proposition_m_formset(request.POST or None, prefix="pm")
    if form.is_valid() and pm_formset.is_valid():
        question = form.save(suffrage=suffrage)
        for qform in pm_formset:
            qform.save(question_m=question)

        return redirect(question.get_absolute_url())

    return render(request, 'vote/ajouterQuestionM.html', { "suffrage": suffrage, "form":form, "pm_formset": pm_formset, }) #"qb_formset":qb_formset, "qm_formset":qm_formset })


class ModifierSuffrage(UpdateView):
    model = Suffrage
    form_class = SuffrageChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Suffrage.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        userProfil = Profil.objects.get(username=self.request.user)
        self.object = form.save(userProfil)
        self.object.date_modification = now()
        self.object.save(self.request.user)
        return redirect(self.object.get_absolute_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierSuffrage, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if self.request.user.estMembre_str(x.abreviation)]
        return form


class ModifierVote(UpdateView):
    model = Vote
    form_class = VoteChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Vote.objects.get(suffrage__slug=self.kwargs['slug'], auteur=self.request.user)

    def form_valid(self, form):
        if self.object.suffrage.get_statut[0] != 0:
            return HttpResponseNotAllowed()
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.object.suffrage.get_absolute_url())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['suffrage'] = Suffrage.objects.get(slug=self.kwargs['slug'])
        return context

class SupprimerSuffrage(DeleteAccess, DeleteView):
    model = Suffrage
    success_url = reverse_lazy('vote:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        if self.object.auteur != self.request.user:
            return redirect(self.object.get_absolute_url)
        return Suffrage.objects.get(slug=self.kwargs['slug'])


@login_required
def lireSuffrage(request, slug):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    if not suffrage.est_autorise(request.user):
        return render(request, 'notMembre.html',)

    try:
        voteCourant = Vote.objects.get(auteur=request.user, suffrage=suffrage)
    except:
        voteCourant = None

    questions_b, questions_m = suffrage.questions

    commentaires = Commentaire.objects.filter(suffrage=suffrage).order_by("date_creation")
    actions = action_object_stream(suffrage)

    form = CommentaireSuffrageForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        if comment:
            comment.suffrage = suffrage
            comment.auteur_comm = request.user
            suffrage.date_dernierMessage = comment.date_creation
            suffrage.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
            suffrage.save()
            comment.save()
            url = suffrage.get_absolute_url() + "#idConversation"
            suffix = "_" + suffrage.asso.abreviation
            #action.send(request.user, verb='suffrage_message' + suffix, action_object=suffrage, url=url,
             #           description="a réagi au suffrage: '%s'" % suffrage.question)

        return redirect(request.path)

    return render(request, 'vote/lireSuffrage.html', {'suffrage': suffrage, 'form': form, 'commentaires':commentaires, 'actions':actions, 'questions_b':questions_b, 'questions_m':questions_m, 'vote':voteCourant},)

@login_required
def resultatsSuffrage(request, slug):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    res_bin, res_majo = suffrage.get_resultats()
    votes = Vote.objects.filter(suffrage=suffrage)
    try:
        vote = Vote.objects.get(suffrage=suffrage, auteur=request.user)
    except:
        vote = ""

    return render(request, 'vote/resultatsSuffrage.html', {
        'suffrage': suffrage, "votes":votes, "res_bin":res_bin, "res_majo": res_majo, 'vote':vote })




@login_required
def lireSuffrage_id(request, id):
    suffrage = get_object_or_404(Suffrage, id=id)
    return lireSuffrage(request, slug=suffrage.slug)


class ModifierCommentaireSuffrage(UpdateView):
    model = Commentaire
    form_class = CommentaireSuffrageChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return Commentaire.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.suffrage.get_absolute_url())


@login_required
def voter(request, slug):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    if not suffrage.est_autorise(request.user):
        return render(request, 'notPermacat.html',)

    if suffrage.get_statut[0] != 0:
        return render(request, 'vote/voteTermine.html',)

    vote = Vote.objects.filter(auteur=request.user, suffrage=suffrage)
    if vote:
        vote.delete()

    questions_b, questions_m = suffrage.questions
    propositions_m, question_m_sp = [], []
    for q in questions_m:
        prop = q.propositions
        if prop :
            propositions_m.append(prop)
        else:
            question_m_sp.append(q)

    propositions_m = suffrage.propositions

    formVote = VoteForm(request.POST or None)

    reponses_b_form = [Reponse_binaire_Form(q, request.POST or None, prefix="rb" + str(i)) for i, q in enumerate(questions_b)]
    reponses_m_form = {(p.question_m, p.id): Reponse_majoritaire_Form(p, request.POST or None, prefix="rp" + str(p.id)) for p in propositions_m}
    #reponses_m_form = [Reponse_majoritaire_Form(p, request.POST or None, prefix="rm_" + str(p.id)) for p in [Proposition_m.objects.filter(question=x) for x in questions_m]]

   #    for p in Proposition_m.objects.filter(question=x):
     #       reponses_m_form += Reponse_majoritaire_Form(x, request.POST or None, prefix="rm_" + str(j) + "_"+ str(p.id))

    if all([f.is_valid() for f in itertools.chain(reponses_b_form, reponses_m_form.values())]) and formVote.is_valid():
        vote = formVote.save(suffrage, request.user)
        for form2 in reponses_b_form:
            form2.save(vote=vote, )
        for form3 in reponses_m_form.values():
            form3.save(vote=vote, )

        return redirect(suffrage.get_absolute_url())

    return render(request, 'vote/voter.html', {'suffrage': suffrage, 'form': formVote, 'reponses_b_form':reponses_b_form, 'reponses_m_form':reponses_m_form},)



class ListeSuffrages(ListView):
    model = Suffrage
    context_object_name = "suffrage_list"
    template_name = "vote/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())

        if "archives" in params and params['archives']:
            qs = Suffrage.objects.filter(estArchive=True)
        else:
            qs = Suffrage.objects.filter(estArchive=False)


        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__abreviation="public")
        else:
            for nomAsso in Choix_global.abreviationsAsso:
                if not getattr(self.request.user, "adherent_" + nomAsso):
                    qs = qs.exclude(asso__abreviation=nomAsso)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "type_vote" in params:
            qs = qs.filter(type_vote=params['type_vote'])
        if "statut" in params:
            if params['statut'] == '0':
                qs = qs.filter(start_time__date__lte=now(), end_time__date__gte=now() )
            if params['statut'] == '1':
                qs = qs.filter(end_time__date__lte=now() )
            if params['statut'] == '2':
                qs = qs.filter(Q(start_time__date__gte=now()))
        if "permacat" in params  and self.request.user.adherent_pc:
            if params['permacat'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'type_vote', 'auteur')

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Suffrage.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Suffrage.objects.order_by('type_vote').values_list('type_vote', flat=True).distinct()
        context['type_vote_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_vote if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="suffrages")

        context['ordreTriPossibles'] = {
                                           "date de création":'-date_creation',
                                           "date du dernier message":'-date_dernierMessage',
                                           "date de la dernière modification":'-date_modification',
                                            "Type de vote":"-type_vote"}

        context['filtresPossibles'] = {
                                           "Vote en cours":'0',
                                           "Vote terminé":'1',
                                           "Vote pas encore démarré":'2',
        }
        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'type_vote' in self.request.GET:
            context['typeFiltre'] = "type_vote"
            try:
                context['type_vote_courant'] = [x[1] for x in Choix.type_vote if x[0] == self.request.GET['type_vote']][0]
            except:
                context['type_vote_courant'] = ""
        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        return context


@login_required
@csrf_exempt
def suivre_suffrages(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='suffrages')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('vote:index')