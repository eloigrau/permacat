# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Atelier, CommentaireAtelier, Choix, Atelier
from .forms import AtelierForm, CommentaireAtelierForm, AtelierChangeForm, AtelierForm, AtelierChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView

from django.utils.timezone import now

from bourseLibre.models import Suivis

def accueil(request):
    return render(request, 'ateliers/accueil.html')


@login_required
def ajouterAtelier(request):
    form = AtelierForm(request.POST or None)
    if form.is_valid():
        atelier = form.save(request.user)
        return redirect(atelier.get_absolute_url())
    return render(request, 'ateliers/atelier_ajouter.html', { "form": form, })


# @login_required
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
        return HttpResponseRedirect(self.object.get_absolute_url())

    def save(self):
        return super(ModifierAtelier, self).save()


class SupprimerAtelier(DeleteView):
    model = Atelier
    success_url = reverse_lazy('ateliers:index_ateliers')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])



@login_required
def lireAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    commentaires = CommentaireAtelier.objects.filter(atelier=atelier).order_by("date_creation")

    form_comment = CommentaireAtelierForm(request.POST or None)
    if form_comment.is_valid():
        comment = form_comment.save(commit=False)
        comment.atelier = atelier
        comment.auteur_comm = request.user
        atelier.date_dernierMessage = comment.date_creation
        atelier.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(comment.commentaire))[:96] + "..."
        atelier.save()
        comment.save()
        return redirect(request.path)

    return render(request, 'ateliers/lireAtelier.html', {'atelier': atelier, 'form': form_comment, 'commentaires':commentaires},)


@login_required
def lireAtelier_id(request, id):
    atelier = get_object_or_404(Atelier, id=id)
    commentaires = CommentaireAtelier.objects.filter(atelier=atelier).order_by("date_creation")

    form_comment = CommentaireAtelierForm(request.POST or None)
    if form_comment.is_valid():
        comment = form_comment.save(commit=False)
        comment.atelier = atelier
        comment.auteur_comm = request.user
        atelier.date_dernierMessage = comment.date_creation
        atelier.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(comment.commentaire))[:96] + "..."
        atelier.save()
        comment.save()
        return redirect(request.path)

    return render(request, 'ateliers/lireAtelier.html', {'atelier': atelier,  'form': form_comment, 'commentaires':commentaires},)


class ListeAteliers(ListView):
    model = Atelier
    context_object_name = "atelier_list"
    template_name = "ateliers/index_ateliers.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        qs = Atelier.objects.all()

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
            qs = qs.order_by('categorie', '-date_dernierMessage', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        cat= Atelier.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_atelier if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles")

        context['ordreTriPossibles'] = ['-date_creation', '-date_dernierMessage', 'categorie', 'titre' ]

        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['categorie_courante'] = [x[1] for x in Choix.type_atelier if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"


        if "mc" in self.request.GET:
            context['typeFiltre'] = "mc"

        return context
