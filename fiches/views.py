# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Fiche, CommentaireFiche, Choix, Atelier
from .forms import FicheForm, CommentaireFicheForm, FicheChangeForm, AtelierForm, AtelierChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView

from django.utils.timezone import now

from bourseLibre.models import Suivis

def accueil(request):
    return render(request, 'fiches/accueil.html')


@login_required
def ajouterFiche(request):
    form = FicheForm(request.POST or None)
    if form.is_valid():
        fiche = form.save(request.user)
        return redirect(fiche.get_absolute_url())
    return render(request, 'fiches/fiche_ajouter.html', { "form": form, })

@login_required
def ajouterAtelier(request, fiche_slug):
    form = AtelierForm(request.POST or None)
    if form.is_valid():
        fiche = Fiche.objects.get(slug=fiche_slug)
        form.save(fiche)
        return redirect(fiche.get_absolute_url())
    return render(request, 'fiches/atelier_ajouter.html', { "form": form, })


# @login_required
class ModifierFiche(UpdateView):
    model = Fiche
    form_class = FicheChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Fiche.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.object.get_absolute_url())

    def save(self):
        return super(ModifierFiche, self).save()

class ModifierAtelier(UpdateView):
    model = Atelier
    form_class = AtelierChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.object.fiche.get_absolute_url())
        #return redirect('lireFiche', slug=self.object.fiche.slug)

    def get_success_url(self):
        return self.object.fiche.get_absolute_url()

    def save(self):
        return super(ModifierAtelier, self).save()

class SupprimerFiche(DeleteView):
    model = Fiche
    success_url = reverse_lazy('fiches:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Fiche.objects.get(slug=self.kwargs['slug'])



@login_required
def lireFiche(request, slug):
    fiche = get_object_or_404(Fiche, slug=slug)

    commentaires = CommentaireFiche.objects.filter(fiche=fiche).order_by("date_creation")
    ateliers = Atelier.objects.filter(fiche=fiche).order_by("date_creation")

    form_comment = CommentaireFicheForm(request.POST or None)
    if form_comment.is_valid():
        comment = form_comment.save(commit=False)
        comment.fiche = fiche
        comment.auteur_comm = request.user
        fiche.date_dernierMessage = comment.date_creation
        fiche.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(comment.commentaire))[:96] + "..."
        fiche.save()
        comment.save()
        return redirect(request.path)

    return render(request, 'fiches/lireFiche.html', {'fiche': fiche, 'ateliers':ateliers, 'form': form_comment, 'commentaires':commentaires},)


@login_required
def lireAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    return render(request, 'fiches/lireAtelier.html', {'atelier': atelier,},)

@login_required
def lireAtelier_id(request, id):
    atelier = get_object_or_404(Atelier, id=id)
    return render(request, 'fiches/lireAtelier.html', {'atelier': atelier,},)

class ListeFiches(ListView):
    model = Fiche
    context_object_name = "fiche_list"
    template_name = "fiches/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        qs = Fiche.objects.all()

        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])

        if "mc" in params:
            if params['mc']=="essentiels":
                qs = qs.filter(tags__name__in=["essentiel",])
            else:
                qs = qs.filter(tags__name__in=[cat for cat in params['mc']])

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('categorie', 'numero', '-date_dernierMessage', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        cat= Fiche.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_fiche if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles")

        context['ordreTriPossibles'] = ['-date_creation', '-date_dernierMessage', 'categorie', 'titre' ]

        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['categorie_courante'] = [x[1] for x in Choix.type_fiche if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"


        if "mc" in self.request.GET:
            context['typeFiltre'] = "mc"

        return context

class ListeAteliers(ListView):
    model = Atelier
    context_object_name = "atelier_list"
    template_name = "fiches/index_ateliers.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        qs = Atelier.objects.all()

        if "categorie" in params:
            qs = qs.filter(fiche__categorie=params['categorie'])

        if "mc" in params:
            if params['mc']=="essentiels":
                qs = qs.filter(fiche__tags__name__in=["essentiel",])
            else:
                qs = qs.filter(fiche__tags__name__in=[cat for cat in params['mc']])

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('fiche__numero', 'fiche__categorie',)

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        cat= Fiche.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_fiche if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles")

        context['ordreTriPossibles'] = ['-date_creation', '-date_dernierMessage', 'categorie', 'titre' ]

        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['categorie_courante'] = [x[1] for x in Choix.type_fiche if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"


        if "mc" in self.request.GET:
            context['typeFiltre'] = "mc"

        return context