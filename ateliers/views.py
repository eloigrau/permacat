# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import CommentaireAtelier, Choix, Atelier, InscriptionAtelier
from .forms import AtelierForm, CommentaireAtelierForm, AtelierChangeForm, ContactParticipantsForm, CommentaireAtelierChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from blog.models import Article
from actstream.models import following
from bourseLibre.settings.production import SERVER_EMAIL
from datetime import timedelta

from django.utils.timezone import now

from bourseLibre.models import Suivis, Profil
from bourseLibre.views_base import DeleteAccess
from bourseLibre.views_admin import send_mass_html_mail

from bourseLibre.constantes import Choix as Choix_global
from actstream import actions, action
from actstream.models import Action as Actstream_action

from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from bs4 import BeautifulSoup

def accueil(request):
    return redirect("ateliers:index_ateliers")
    #return render(request, 'ateliers/accueil.html')


@login_required
def ajouterAtelier(request, article_slug=None):
    form = AtelierForm(request, request.POST or None)
    if article_slug:
        article = Article.objects.get(slug=article_slug)
    else:
        article = None
    if form.is_valid():
        atelier = form.save(request, article)
        action.send(request.user, verb='atelier_nouveau', action_object=atelier, url=atelier.get_absolute_url(),
                     description="a ajouté l'atelier: '%s'" % atelier.titre)
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
        if self.object.date_modification - self.object.date_creation > timedelta(minutes=10):
            action.send(self.request.user, verb='atelier_modifier', action_object=self.object, url=self.object.get_absolute_url(),
                         description="a modifié l'atelier: '%s'" % self.object.titre)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def save(self):
        return super(ModifierAtelier, self).save()

    def get_form(self, *args, **kwargs):
        form = super(ModifierAtelier, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [x for i, x in enumerate(form.fields["asso"].choices) if
                                        self.request.user.estMembre_str(x[1])]
        return form

class SupprimerAtelier(DeleteAccess, DeleteView):
    model = Atelier
    success_url = reverse_lazy('ateliers:index_ateliers')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])

@login_required
def inscriptionAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    if not InscriptionAtelier.objects.filter(user=request.user, atelier=atelier):
        inscript = InscriptionAtelier(user=request.user, atelier=atelier)
        inscript.save()
        action.send(request.user, verb='atelier_inscription', action_object=atelier, url=atelier.get_absolute_url(),
                     description="s'est inscrit.e à l'atelier: '%s'" % atelier.titre)
    #messages.info(request, 'Vous êtes bien inscrit.e à cet atelier !')
    return redirect(atelier.get_absolute_url())

@login_required
def annulerInscription(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    inscript = InscriptionAtelier.objects.filter(user=request.user, atelier=atelier)
    inscript.delete()
    action.send(request.user, verb='atelier_désinscription', action_object=atelier, url=atelier.get_absolute_url(),
                 description="s'est désinscrit de l'atelier: '%s'" % atelier.titre)
    return redirect(atelier.get_absolute_url())

@login_required
def contacterParticipantsAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    form = ContactParticipantsForm(request.POST or None, )
    inscrits = [x[0] for x in InscriptionAtelier.objects.filter(atelier=atelier).values_list('user__email')]
    referent = Profil.objects.get(username=atelier.referent)
    inscrits.append(referent.email)
    if form.is_valid():
        sujet = "[Permacat] Au sujet de l'atelier Permacat '" + atelier.titre +"' "
        message_html = str(request.user.username) + " ("+ str(request.user.email)+") a écrit le message suivant aux participants : \n"
        message_html += form.cleaned_data['msg']
        message_html += "\n (ne pas répondre à ce message, utiliser <a href='https://www.perma.cat"+ atelier.get_absolute_url() +" '>l'atelier sur le site perma.cat</a> :)"
        messagetxt = BeautifulSoup(message_html).get_text()
        send_mass_html_mail([(sujet, messagetxt, message_html, SERVER_EMAIL, inscrits) ], fail_silently=False)

    return render(request, 'ateliers/contacterParticipantsAtelier.html', {'atelier': atelier,  'form': form,  'inscrits':inscrits})


@login_required
def lireAtelier_slug(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    return lireAtelier(request, atelier)

@login_required
def lireAtelier_id(request, id):
    atelier = get_object_or_404(Atelier, id=id)
    return lireAtelier(request, atelier)

@login_required
def lireAtelier(request, atelier):
    commentaires = CommentaireAtelier.objects.filter(atelier=atelier).order_by("date_creation")
    inscrits = [x[0] for x in InscriptionAtelier.objects.filter(atelier=atelier).values_list('user__username')]

    if not request.user.is_anonymous:
        user_inscrit = request.user.username in inscrits
    else:
        user_inscrit = []


    hit_count = HitCount.objects.get_for_object(atelier)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)

    form_comment = CommentaireAtelierForm(request.POST or None)
    if form_comment.is_valid():
        comment = form_comment.save(commit=False)
        comment.atelier = atelier
        comment.auteur_comm = request.user
        atelier.date_dernierMessage = comment.date_creation
        atelier.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(comment.commentaire))[:96] + "..."
        atelier.save()
        comment.save()

        action.send(request.user, verb='atelier_message', url=atelier.get_absolute_url(),
                    description="a commenté l'atelier: '%s'" % atelier.titre)
        emails = [Profil.objects.get(username=atelier.auteur).email, ] + [x.user.email for x in InscriptionAtelier.objects.filter(atelier=atelier)]
        message = "L'atelier <a href='https://www.perma.cat" + atelier.get_absolute_url() + "'>%s</a> a été commenté" %atelier.titre
        action.send(request.user, verb='emails', url=atelier.get_absolute_url(),
                    titre="a commenté l'atelier: '%s'" % atelier.titre,  message=message, emails=emails)

        return redirect(request.path)

    return render(request, 'ateliers/lireAtelier.html', {'atelier': atelier,  'form': form_comment, 'commentaires':commentaires, 'user_inscrit': user_inscrit, 'inscrits': inscrits},)


class ListeAteliers(ListView):
    model = Atelier
    context_object_name = "atelier_list"
    template_name = "ateliers/index_ateliers.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        self.qs = Atelier.objects.filter(estArchive=False)

        if "categorie" in params:
            self.qs = self.qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            self.qs = self.qs.order_by(params['ordreTri'])
        else:
            self.qs = self.qs.order_by('-start_time', 'categorie', '-date_dernierMessage', )

        return self.qs.filter(start_time__gte=now(), start_time__isnull=False).order_by('-start_time')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['list_archive'] = Atelier.objects.filter(estArchive=True).order_by('-start_time')
        context['list_propositions'] = self.qs.filter(start_time__isnull=True).order_by('-start_time')
        context['list_passes'] = self.qs.filter(start_time__lt=now(), start_time__isnull=False).order_by('-start_time')

        cat= Atelier.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_atelier if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="ateliers")

        context['ordreTriPossibles'] = ['-date_creation', '-date_dernierMessage', 'categorie', 'titre' ]

        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['categorie_courante'] = [x[1] for x in Choix.type_atelier if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"


        if "mc" in self.request.GET:
            context['typeFiltre'] = "mc"

        return context



class ModifierCommentaire(UpdateView):
    model = CommentaireAtelier
    form_class = CommentaireAtelierChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return CommentaireAtelier.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return redirect(self.object)



@login_required
@csrf_exempt
def suivre_ateliers(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='ateliers')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('ateliers:index_ateliers')