# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from .models import Suffrage, Commentaire, Choix, Vote
from .forms import SuffrageForm, CommentaireSuffrageForm, CommentaireSuffrageChangeForm, SuffrageChangeForm, \
    VoteForm, VoteChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.utils.timezone import now
from django.db.models import Q
from actstream import actions, action
from actstream.models import followers, following, action_object_stream
from bourseLibre.models import Suivis, Profil
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotAllowed

def accueil(request):
    return render(request, 'vote/accueil.html')


@login_required
def ajouterSuffrage(request):
    form = SuffrageForm(request.POST or None)
    if form.is_valid():
        suffrage = form.save(request.user)
        url = suffrage.get_absolute_url()
        suffix = "" if suffrage.estPublic else "_permacat"
        action.send(request.user, verb='suffrage_ajout'+suffix, action_object=suffrage, url=url,
                    description="a ajouté un suffrage : '%s'" % suffrage.question)

        return redirect(suffrage.get_absolute_url())

    return render(request, 'vote/ajouterSuffrage.html', { "form": form, })


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

class SupprimerSuffrage(DeleteView):
    model = Suffrage
    success_url = reverse_lazy('vote:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Suffrage.objects.get(slug=self.kwargs['slug'])



@login_required
def lireSuffrage(request, slug):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    try:
        voteCourant = Vote.objects.get(auteur=request.user, suffrage=suffrage)
    except:
        voteCourant = None
    if not suffrage.estPublic and not request.user.is_permacat:
        return render(request, 'notPermacat.html',)

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
            suffix = "_permacat" if not suffrage.estPublic else ""
            action.send(request.user, verb='suffrage_message' + suffix, action_object=suffrage, url=url,
                        description="a réagi au suffrage: '%s'" % suffrage.question)

        return redirect(request.path)

    return render(request, 'vote/lireSuffrage.html', {'suffrage': suffrage, 'form': form, 'commentaires':commentaires, 'actions':actions, 'vote':voteCourant},)

@login_required
def resultatsSuffrage(request, slug):
    suffrage = get_object_or_404(Suffrage, slug=slug)
    resultats = suffrage.getResultats()
    try:
        vote = Vote.objects.get(suffrage=suffrage, auteur=request.user)
    except:
        vote = ""

    return render(request, 'vote/resultatsSuffrage.html', {
        'suffrage': suffrage,
        'nbOui':resultats['nbOui'], 'nbNon':resultats['nbNon'], 'nbNSPP':resultats['nbNSPP'], 'nbTotal':resultats['nbTotal'], 'resultat':resultats['resultat'], 'vote':vote, 'votes':resultats['votes'] },)



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
    if not suffrage.estPublic and not request.user.is_permacat:
        return render(request, 'notPermacat.html',)

    if suffrage.get_statut[0] != 0:
        return render(request, 'vote/voteTermine.html',)

    vote = Vote.objects.filter(auteur=request.user, suffrage=suffrage)
    if vote:
        return render(request, 'vote/dejaVote.html',)

    form = VoteForm(request.POST or None)

    if form.is_valid():
        form.save(suffrage, request.user)
        return redirect(suffrage.get_absolute_url())

    return render(request, 'vote/voter.html', {'suffrage': suffrage, 'form': form},)



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