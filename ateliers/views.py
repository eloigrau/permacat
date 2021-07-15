# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import CommentaireAtelier, Choix, Atelier, InscriptionAtelier
from .forms import AtelierForm, CommentaireAtelierForm, AtelierChangeForm, ContactParticipantsForm, CommentaireAtelierChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from blog.models import Article

from django.utils.timezone import now

from bourseLibre.models import Suivis, Profil

from bourseLibre.constantes import Choix as Choix_global
from actstream import actions, action

from hitcount.models import HitCount
from hitcount.views import HitCountMixin

def accueil(request):
    return redirect("ateliers:index_ateliers")
    #return render(request, 'ateliers/accueil.html')


@login_required
def ajouterAtelier(request, article_slug=None):
    form = AtelierForm(request, request.POST or None)
    if article_slug:
        article = Article.objects.get(slug=article_slug)
    else:
        article=None
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

class SupprimerAtelier(DeleteView):
    model = Atelier
    success_url = reverse_lazy('ateliers:index_ateliers')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])



@login_required
def inscriptionAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    inscript = InscriptionAtelier(user=request.user, atelier=atelier)
    inscript.save()
    action.send(request.user, verb='atelier_inscription', action_object=atelier, url=atelier.get_absolute_url(),
                 description="s'est inscrit.e à l'atelier: '%s'" % atelier.titre)
    #messages.info(request, 'Vous êtes bien inscrit à cet atelier !')
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
    if form.is_valid():
        sujet = "[Permacat] Au sujet de l'atelier Permacat '" + atelier.titre +"'"
        inscrits = [x[0] for x in InscriptionAtelier.objects.filter(atelier=atelier).values_list('user__email')]
        referent = Profil.objects.get(username=atelier.referent)
        inscrits.append(referent)
        message_html = form.cleaned_data['msg']
        try:
            send_mail(sujet, message_html,
                      request.user.email, inscrits, fail_silently=False,
                      html_message=message_html)

            if form.cleaned_data['renvoi']:
                send_mail(sujet,
                          "Vous avez envoyé aux participants de l'atelier Permacat '" + atelier.titre +"' le message suivant : " + message_html,
                          request.user.email, [request.user.email, ], fail_silently=False,
                          html_message=message_html)

            return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataire": "".join(inscrits)})
        except BadHeaderError:
            return render(request, 'erreur.html', {'msg': 'Invalid header found.'})

        return render(request, 'erreur.html', {'msg': "Désolé, une erreur s'est produite lors de l'envoie du mail..."})

    return render(request, 'ateliers/contacterParticipantsAtelier.html', {'atelier': atelier,  'form': form,  })


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
        action.send(request.user, verb='atelier_message', action_object=atelier, url=atelier.get_absolute_url(),
                    description="a réagi à la fiche: '%s'" % atelier.titre)

        return redirect(request.path)

    return render(request, 'ateliers/lireAtelier.html', {'atelier': atelier,  'form': form_comment, 'commentaires':commentaires, 'user_inscrit': user_inscrit, 'inscrits': inscrits},)


class ListeAteliers(ListView):
    model = Atelier
    context_object_name = "atelier_list"
    template_name = "ateliers/index_ateliers.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        qs = Atelier.objects.filter(estArchive=False)

        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])

        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__nom="public")
        else:
            for nomAsso in Choix_global.abreviationsAsso:
                if not getattr(self.request.user, "adherent_" + nomAsso):
                    qs = qs.exclude(asso__abreviation=nomAsso)


        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-start_time', 'categorie', '-date_dernierMessage', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['list_archive'] = Atelier.objects.filter(estArchive=True)

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



class ModifierCommentaire(UpdateView):
    model = CommentaireAtelier
    form_class = CommentaireAtelierChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return CommentaireAtelier.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.object.atelier.get_absolute_url())
