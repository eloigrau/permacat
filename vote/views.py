# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from .models import Votation, Commentaire, Choix, Vote
from .forms import VotationForm, CommentaireVotationForm, CommentaireVotationChangeForm, VotationChangeForm, \
    VoteForm, VoteChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import action
from actstream.models import action_object_stream
from django.utils.timezone import now
from django.db.models import Q

#from django.contrib.contenttypes.models import ContentType
from bourseLibre.models import Suivis
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin

def accueil(request):
    return render(request, 'vote/accueil.html')


@login_required
def ajouterVotation(request):
    try:
        form = VotationForm(request.POST or None)
        if form.is_valid():
            votation = form.save(request.user)
            url = votation.get_absolute_url()
            suffix = "" if votation.estPublic else "_permacat"
            action.send(request.user, verb='votation_nouveau'+suffix, action_object=votation, url=url,
                        description="a ajouté une votation : '%s'" % votation.titre)
            return redirect(votation.get_absolute_url())

    except Exception as inst:
        print(inst)
    return render(request, 'vote/ajouterVotation.html', { "form": form, })


class ModifierVotation(UpdateView):
    model = Votation
    form_class = VotationChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Votation.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return redirect(self.object.get_absolute_url())


class ModifierVote(UpdateView):
    model = Vote
    form_class = VoteChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Vote.objects.get(votation__slug=self.kwargs['slug'], auteur=self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.object.votation.get_absolute_url())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['votation'] = Votation.objects.get(slug=self.kwargs['slug'])
        return context

class SupprimerVotation(DeleteView):
    model = Votation
    success_url = reverse_lazy('vote:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Votation.objects.get(slug=self.kwargs['slug'])



@login_required
def lireVotation(request, slug):
    votation = get_object_or_404(Votation, slug=slug)
    try:
        vote = Vote.objects.get(auteur=request.user, votation=votation)
    except:
        vote = None
    if not votation.estPublic and not request.user.is_permacat:
        return render(request, 'notPermacat.html',)

    commentaires = Commentaire.objects.filter(votation=votation).order_by("date_creation")

    actions = action_object_stream(votation)

    form = CommentaireVotationForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        if comment:
            comment.votation = votation
            comment.auteur_comm = request.user
            votation.date_dernierMessage = comment.date_creation
            votation.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
            votation.save()
            comment.save()
            url = votation.get_absolute_url() + "#idConversation"
            suffix = "_permacat" if not votation.estPublic else ""
            action.send(request.user, verb='article_message' + suffix, action_object=votation, url=url,
                        description="a réagi à la votation: '%s'" % votation.titre)

        return redirect(request.path)

    return render(request, 'vote/lireVotation.html', {'votation': votation, 'form': form, 'commentaires':commentaires, 'actions':actions, 'vote':vote},)

@login_required
def resultatsVotation(request, slug):
    votation = get_object_or_404(Votation, slug=slug)
    resultats = votation.getResultats()
    try:
        vote = Vote.objects.get(votation=votation, auteur=request.user)
    except:
        vote = ""

    return render(request, 'vote/resultatsVotation.html', {
        'votation': votation,
        'nbOui':resultats['nbOui'], 'nbNon':resultats['nbNon'], 'nbNSPP':resultats['nbNSPP'], 'nbTotal':resultats['nbTotal'], 'resultat':resultats['resultat'], 'vote':vote, 'votes':resultats['votes'] },)



@login_required
def lireVotation_id(request, id):
    votation = get_object_or_404(Votation, id=id)
    return lireVotation(request, slug=votation.slug)


class ModifierCommentaireVotation(UpdateView):
    model = Commentaire
    form_class = CommentaireVotationChangeForm
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
        return HttpResponseRedirect(self.object.votation.get_absolute_url())


@login_required
def voter(request, slug):
    votation = get_object_or_404(Votation, slug=slug)
    if not votation.estPublic and not request.user.is_permacat:
        return render(request, 'notPermacat.html',)

    if votation.get_statut[0] != 0:
        return render(request, 'vote/voteTermine.html',)

    vote = Vote.objects.filter(auteur=request.user, votation=votation)
    if vote:
        return render(request, 'vote/dejaVote.html',)

    form = VoteForm(request.POST or None)

    if form.is_valid():
        form.save(votation, request.user)
        return redirect(votation.get_absolute_url())

    return render(request, 'vote/voter.html', {'votation': votation, 'form': form},)



class ListeVotations(ListView):
    model = Votation
    context_object_name = "votation_list"
    template_name = "vote/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())

        if "archives" in params and params['archives']:
            qs = Votation.objects.filter(estArchive=True)
        else:
            qs = Votation.objects.filter(estArchive=False)

        if not self.request.user.is_authenticated or not self.request.user.is_permacat:
            qs = qs.filter(estPublic=True)

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
        if "permacat" in params  and self.request.user.is_permacat:
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
        context['auteur_list'] = Votation.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Votation.objects.order_by('type_vote').values_list('type_vote', flat=True).distinct()
        context['type_vote_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_vote if x[0] in cat]
        context['typeFiltre'] = "aucun"

        context['ordreTriPossibles'] = {
                                           "date de création":'-date_creation',
                                           "date du dernier message":'-date_dernierMessage',
                                           "date de la dernière modification":'-date_modification',
                                            "titre": 'titre' }

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
