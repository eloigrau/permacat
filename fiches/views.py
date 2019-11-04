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
        return render(request, 'fiches/lireFiche.html', {'fiche': fiche})
    return render(request, 'fiches/fiche_ajouter.html', { "form": form, })

@login_required
def ajouterAtelier(request, fiche_slug):
    form = AtelierForm(request.POST or None)
    if form.is_valid():
        fiche = Fiche.objects.get(slug=fiche_slug)
        atelier = form.save(fiche)
        return render(request, 'fiches/lireFiche.html', {'fiche': atelier.fiche})
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
        return HttpResponseRedirect(self.get_success_url())


    def save(self):
        return super(ModifierFiche, self).save()

class ModifierAtelier(UpdateView):
    model = Atelier
    form_class = AtelierChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


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


class ListeFiches(ListView):
    model = Fiche
    context_object_name = "fiche_list"
    template_name = "fiches/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        qs = Fiche.objects.all()

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'categorie')

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
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        return context
