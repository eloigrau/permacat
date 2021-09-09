# -*- coding: utf-8 -*-
'''
Created on 25 mai 2017

@author: tchenrezi
'''
import itertools

from django.shortcuts import HttpResponseRedirect, render, redirect, get_object_or_404#, render, redirect, render_to_response,
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .forms import Produit_aliment_CreationForm, Produit_vegetal_CreationForm, Produit_objet_CreationForm, \
    Produit_service_CreationForm, ContactForm, AdresseForm, ProfilCreationForm, MessageForm, MessageGeneralForm, \
    ProducteurChangeForm, Produit_aliment_modifier_form, Produit_service_modifier_form, \
    Produit_objet_modifier_form, Produit_vegetal_modifier_form, ChercherConversationForm, InscriptionNewsletterForm, \
    MessageChangeForm, ContactMailForm
from .models import Profil, Produit, Adresse, Choix, Panier, Item, Asso, get_categorie_from_subcat, Conversation, Message, \
    MessageGeneral, getOrCreateConversation, Suivis, InscriptionNewsletter
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.core.mail import mail_admins, send_mail, BadHeaderError, send_mass_mail
from django_summernote.widgets import SummernoteWidget
from random import choice
from datetime import date, timedelta, datetime
from django.http import HttpResponse
from django import forms
from django.http import Http404

from blog.models import Article, Projet, EvenementAcceuil, Evenement
from ateliers.models import Atelier
from vote.models import Suffrage, Vote
from jardinpartage.models import Article as Article_jardin

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.debug import sensitive_variables
#from django.views.decorators.debug import sensitive_post_parameters

#from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, CharField, F
from django.db.models.functions import Lower
from django.utils.html import strip_tags

from actstream import actions, action
from actstream.models import Action, Follow, following, followers, actor_stream,  any_stream, user_stream, action_object_stream, model_stream, target_stream
#from fcm_django.models import FCMDevice
# from django.http.response import JsonResponse, HttpResponse
# from django.views.decorators.http import require_GET, require_POST
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
# from django.views.decorators.csrf import csrf_exempt
# from webpush import send_user_notification
# import json
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ObjectDoesNotExist
from bourseLibre.settings.production import SERVER_EMAIL
from bourseLibre.settings import LOCALL
from bourseLibre.constantes import Choix as Choix_global
from django.utils.timezone import now
import pytz

CharField.register_lookup(Lower, "lower")

from .views_notifications import getNbNewNotifications
from bourseLibre.views_base import DeleteAccess
from itertools import chain


def getEvenementsSemaine(request):
    current_week = date.today().isocalendar()[1]
    current_year = date.today().isocalendar()[0]
    evenements = []

    if not request.user.is_anonymous:
        ev = Evenement.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')

        for nomAsso in Choix_global.abreviationsAsso:
            ev = ev.exclude(article__asso__abreviation=nomAsso)
        evenements = []

        ev_art = Evenement.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                ev_art = ev_art.exclude(article__asso__abreviation=nomAsso)
        evenements.append(ev_art)

        ev_2 = Article.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                ev_2 = ev_2.exclude(asso__abreviation=nomAsso)

        evenements.append(ev_2)
        ev_3= []
        if request.user.adherent_jp:
            ev_3 = Article_jardin.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')
            evenements.append(ev_3)

        ev_4 = Projet.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                ev_4 = ev_4.exclude(asso__abreviation=nomAsso)
        evenements.append(ev_4)


        ev_5 = Atelier.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                ev_5 = ev_5.exclude(asso__abreviation=nomAsso)

        evenements.append(ev_5)
        utc = pytz.UTC
        y = []
        for ev in list(chain(ev_art, ev_2, ev_3, ev_4, ev_5)):
            try:
                y.append((ev, date(ev.start_time.year, ev.start_time.month, ev.start_time.day)))
            except:
                pass
        eve = sorted(y, key=lambda x:x[1])
        evenements = [x for x, y in eve]

    return evenements

def bienvenue(request):
    nums = ['01', '02', '03', '04', '07', '10', '11', '13', '15', '17', '20', '21', '23', ]
    nomImage = 'img/flo/resized0' + choice(nums)+'.png'
    nbNotif = 0
    nbExpires = 0
    utc = pytz.UTC
    yesterday = (datetime.now() - timedelta(hours=12)).replace(tzinfo=utc)
    evenements = EvenementAcceuil.objects.filter(date__gt=yesterday).order_by('date')
    evenements_semaine = getEvenementsSemaine(request)
    if request.user.is_authenticated:
        nbNotif = getNbNewNotifications(request)
        nbExpires = getNbProduits_expires(request)

    if not request.user.is_anonymous:
        suffrages = Suffrage.objects.filter(start_time__lte=datetime.now(), end_time__gte=datetime.now())
        votes = []
        for vote in suffrages:
            if vote.est_autorise(request.user):
                votes.append([vote, len(Vote.objects.filter(suffrage=vote, auteur=request.user))])

        derniers_articles = Article.objects.filter(estArchive=False).order_by('-id')
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                derniers_articles = derniers_articles.exclude(asso__abreviation=nomAsso)

        derniers_articles_comm = Article.objects.filter(estArchive=False, dernierMessage__isnull=False).order_by(
            'date_dernierMessage')

        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                derniers_articles_comm = derniers_articles_comm.exclude(asso__abreviation=nomAsso)

        derniers_articles_modif = Article.objects.filter(Q(estArchive=False) & Q(date_modification__isnull=False) & ~Q(
            date_modification=F("date_creation"))).order_by('date_modification')

        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                derniers_articles_modif = derniers_articles_modif.exclude(asso__abreviation=nomAsso)
    else:
        derniers_articles, derniers_articles_comm, derniers_articles_modif, votes = [], [], [], []

    derniers = sorted(set([x for x in itertools.chain(derniers_articles_comm[::-1][:8], derniers_articles_modif[::-1][:8], derniers_articles[:8], )]), key=lambda x:x.date_modification if x.date_modification else x.date_creation)[::-1]

    return render(request, 'bienvenue.html', {'nomImage':nomImage, "nbNotif": nbNotif , "nbExpires":nbExpires, "evenements":evenements, "evenements_semaine":evenements_semaine, "derniers_articles":derniers, 'votes':votes})

class MyException(Exception):
    pass

    #return render(request, 'notMembre.html', {'asso':assos } )

def testIsMembreAsso(request, asso):
    if asso == "public":
        return Asso.objects.get(nom="Public")

    assos = Asso.objects.filter(Q(nom=asso) | Q(abreviation=asso))
    if assos:
        assos = assos[0]

        if not assos.is_membre(request.user) and not request.user.is_superuser:
            return render(request, 'notMembre.html', {'asso':assos } )
        return assos
    return Asso.objects.get(nom="Public")



@login_required
def produit_proposer(request, type_produit):
    try:
        bgcolor = Choix.couleurs[type_produit]
    except:
        bgcolor = None

    if type_produit == 'aliment':
        type_form = Produit_aliment_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'vegetal':
        type_form = Produit_vegetal_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'service':
        type_form = Produit_service_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'objet':
        type_form = Produit_objet_CreationForm(request, request.POST or None, request.FILES or None)
    else:
        raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')

    if type_form.is_valid():
       # produit = produit_form.save(commit=False)
        produit = type_form.save(commit=False)
        produit.user = request.user
        produit.categorie = type_produit

        produit.save()
        url = produit.get_absolute_url()
        suffix = "_" + produit.asso.abreviation
        offreOuDemande = "offre" if produit.estUneOffre else "demande"
        action.send(request.user, verb='ajout_offre'+suffix, action_object=produit, url=url,
                    description="a ajouté une "+offreOuDemande+" au marché : '%s'" %(produit.nom_produit))

        messages.info(request, 'Votre offre a été ajoutée au marché, merci !')
        return HttpResponseRedirect('/marche/detail/' + str(produit.id))
    return render(request, 'bourseLibre/produit_proposer.html', {"form": type_form, "bgcolor": bgcolor, "type_produit":type_produit})


class ProduitModifier(UpdateView):
    model = Produit
    template_name_suffix = '_modifier'
    fields = ['date_debut', 'date_expiration', 'nom_produit', 'description', 'prix', 'unite_prix', 'souscategorie', 'estUneOffre', 'estPublic', 'type_prix']# 'souscategorie','etat','type_prix']

    widgets = {
        'date_debut': forms.DateInput(attrs={'type': "date"}),
        'date_expiration': forms.DateInput(attrs={'type': "date"}),
        'description': SummernoteWidget(),
    }


    def get_form_class(self):
        if self.object.categorie == 'aliment':
            return Produit_aliment_modifier_form
        elif self.object.categorie == 'vegetal':
            return Produit_vegetal_modifier_form
        elif self.object.categorie == 'service':
            return Produit_service_modifier_form
        elif self.object.categorie == 'objet':
            return Produit_objet_modifier_form
        else:
            raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')

    def get_queryset(self):
        return self.model.objects.select_subclasses()

    def get_form_kwargs(self):
        kwargs = super(ProduitModifier, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_form(self, *args, **kwargs):
        form = super(ProduitModifier, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [x for i, x in enumerate(form.fields["asso"].choices) if
                                       self.request.user.estMembre_str(x[1])]

        return form

            # @login_required

class ProduitSupprimer(DeleteAccess, DeleteView):
    model = Produit
    success_url = reverse_lazy('marche')

@login_required
def proposerProduit_entree(request):
    return render(request, 'bourseLibre/produit_proposer_entree.html', {"couleurs":Choix.couleurs})


@login_required
def detailProduit(request, produit_id):
    try:
        prod = Produit.objects.get_subclass(id=produit_id)
    except ObjectDoesNotExist:
        raise Http404

    if not prod.est_autorise(request.user):
        return render(request, 'notMembre.html',{"asso":prod.asso})
    return render(request, 'bourseLibre/produit_detail.html', {'produit': prod})


def merci(request, template_name='merci.html'):
    return render(request, template_name)


@login_required
def profil_courant(request, ):
    nbExpires = getNbProduits_expires(request)
    return render(request, 'profil.html', {'user': request.user, "nbExpires":nbExpires})


@login_required
def profil(request, user_id):
    try:
        user = Profil.objects.get(id=user_id)
        distance = user.getDistance(request.user)
        return render(request, 'profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
            return render(request, 'profil_inconnu.html', {'userid': user_id})

@login_required
def annuaire(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    prof = asso.getProfils()
    nb_profils = len(prof)
    prof = prof.filter(accepter_annuaire=True)
    return render(request, 'annuaire.html', {'profils':prof, "nb_profils":nb_profils, "asso":asso} )

@login_required
def listeContacts(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    if request.user.is_superuser:
        listeMails = [
            {"type":'user_newsletter' ,"profils":Profil.objects.filter(inscrit_newsletter=True), "titre":"Liste des inscrits à la newsletter : "},
        {"type":'anonym_newsletter' ,"profils":InscriptionNewsletter.objects.all(), "titre":"Liste des inscrits anonymes à la newsletter : "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_pc=True), "titre":"Liste des adhérents Permacat: "},
           # {"type":'user_futur_adherent', "profils":Profil.objects.filter(statut_adhesion=0), "titre":"Liste des personnes qui veulent adhérer à Permacat :"}
        ]
    else:
        listeMails = [
          {"type":'user_adherent' , "profils":Profil.objects.filter(adherent_pc=True), "titre":"Liste des adhérents Permacat: "},
           # {"type":'user_futur_adherent', "profils":Profil.objects.filter(statut_adhesion=0), "titre":"Liste des personnes qui veulent adhérer à Permacat :"}
        ]

    return render(request, 'listeContacts.html', {"listeMails":listeMails, "asso":asso })

@login_required
def listeContacts_admin(request):
    if request.user.is_superuser:
        listeMails = [
            {"type":'user_newsletter' ,"profils":Profil.objects.all(), "titre":"Liste des inscrits au site : "},
        {"type":'anonym_newsletter' ,"profils":InscriptionNewsletter.objects.all(), "titre":"Liste des inscrits anonymes à la newsletter : "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_pc=True), "titre":"Liste des adhérents Permacat: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_rtg=True), "titre":"Liste des adhérents RTG: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_scic=True), "titre":"Liste des adhérents PermAgora: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_citealt=True), "titre":"Liste des adhérents Cite Altruiste: "},
           # {"type":'user_futur_adherent', "profils":Profil.objects.filter(statut_adhesion=0), "titre":"Liste des personnes qui veulent adhérer à Permacat :"}
        ]
    else:
        listeMails = [ ]

    return render(request, 'listeContacts.html', {"listeMails":listeMails})

@login_required
def listeFollowers(request, asso):
    asso=testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    listeArticles = []
    for art in Article.objects.all():
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })
    for art in Article_jardin.objects.all():
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })
    for art in Projet.objects.all():
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })

    return render(request, 'listeFollowers.html', {"listeArticles":listeArticles})



@login_required
def admin_asso(request, asso):
    asso=testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    listeFichers = []
    if asso == 'permacat':
        listeFichers = [
            {"titre": "Télécharger le bilan comptable", "url": "{{STATIC_ROOT]]/admin/coucou.txt"},
            {"titre":"Télécharger un RIB", "url":"{{STATIC_ROOT]]/admin/bilan.txt" },
            {"titre":"Télécharger les statuts et règlement intérieur", "url":"{{STATIC_ROOT]]/admin/statuts.txt" },
        ]
    return render(request, 'asso/admin_asso.html', {"listeFichers":listeFichers, "asso":asso} )

@login_required
def admin_asso_rtg(request):
    if not request.user.adherent_rtg:
        return render(request, "notRTG.html")

    listeFichers = [
    ]
    return render(request, 'asso/admin_asso_rtg.html', {"listeFichers":listeFichers} )


def presentation_asso(request, asso):
    return render(request, 'asso/'+ asso + "/presentation_asso.html")

def presentation_groupes(request):
    return render(request, 'asso/presentation_groupes.html')

@login_required
def telechargements_asso(request):
    if not request.user.adherent_pc:
        return render(request, "notPermacat.html")

    fichiers = [{'titre' : 'Contrat credit mutuel', 'url': static('doc/contrat_credit_mutuel.pdf'),},
                {'titre' : 'Procès verbal de constitution', 'url': static('doc/PV_constitution.pdf'),},
                {'titre' : "Recepissé de création de l'asso", 'url': static('doc/recepisse_creation.pdf'),},
                {'titre' : "Publication au journal officiel", 'url': static('doc/JOAFE_PDF_Unitaire_20190012_01238.pdf'),},
                {'titre' : 'Statuts déposés', 'url': static('doc/statuts.pdf'),},
                {'titre' : 'RIB', 'url': static('doc/rib.pdf'),},
                {'titre' : 'CR AGO 2021', 'url': static('doc/CR/2021_AGO-Compte_rendu.pdf'),},
                {'titre' : 'CR Réunion écovillage 16/04/2021', 'url': static('doc/CR/CR16AVRIL21_ecovillage.docx'),},
                ]
    return render(request, 'asso/fichiers.html', {'fichiers':fichiers})


def adhesion_entree(request):
    return render(request, 'asso/adhesion.html', )


def adhesion_asso(request, asso):
    asso = Asso.objects.get(Q(nom=asso) | Q(abreviation=asso))
    return render(request, 'asso/'+ asso.abreviation +'/adhesion.html', )


def fairedon_asso(request, asso):
    if asso == 'developpeur':
        return render(request, 'asso/fairedondeveloppeur.html', )

    asso = Asso.objects.get(Q(nom=asso) | Q(abreviation=asso))

    return render(request, 'asso/'+ asso.abreviation +'/fairedon.html', )

@login_required
def carte(request, asso):
    asso=testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    profils = asso.getProfils_Annuaire()
    if asso.abreviation == "public":
        titre = "Carte des coopérateurs du site*"
    else:
        titre = "Carte des membres du groupe " + asso.nom + "*"

    try:
        import simplejson
        import requests
        url = "https://presdecheznous.gogocarto.fr/api/elements.json?limit=500&bounds=1.75232%2C42.31794%2C3.24646%2C42.94034"

        reponse = requests.get(url)
        data = simplejson.loads(reponse.text)
        ev = data["data"]
    except:
        ev = []

    return render(request, 'carte_cooperateurs.html', {'profils':profils, 'titre': titre, 'data':ev, "asso":asso} )


# @login_required
# def carte(request, asso):
#     asso = testIsMembreAsso(request, asso)
#     if not isinstance(asso, Asso):
#         raise PermissionDenied
#     profils = asso.getProfilsAnnuaire().filter(accepter_annuaire=True).order_by("username")
#     return render(request, 'carte_cooperateurs.html', {'profils':profils, 'titre': "Carte des adhérents "+str(asso) + "*" } )

@login_required
def profil_contact(request, user_id):
    recepteur = Profil.objects.get(id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[permacat] "+ request.user.username + "(" + request.user.email+ ") vous a écrit: "+ form.cleaned_data['sujet']
            message_txt = ""
            message_html = form.cleaned_data['msg']
            recepteurs = [recepteur.email,]
            if form.cleaned_data['renvoi'] :
                recepteurs = [recepteur.email, request.user.email]

            send_mail(
                sujet,
                message_txt,
                request.user.email,
                recepteurs,
                html_message=message_html,
                fail_silently=False,
                )
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg':message_html, 'envoyeur':request.user.username + " (" + request.user.email + ")", "destinataire":recepteur.username + " (" +recepteur.email+ ")"})
    else:
        form = ContactForm()
    return render(request, 'contact/profil_contact.html', {'form': form, 'recepteur':recepteur})

    #message = None
    #titre = None
    # id_panier = request.GET.get('panier')
    # if id_panier:
    #     panier = Panier.objects.get(id=id_panier)
    #     message = panier.get_message_demande(int(user_id))
    #     titre = "Proposition d'échange"
    #
    # id_produit = request.GET.get('produit')
    # if id_produit:
    #     produit = Produit.objects.get(id=id_produit)
    #     message = produit.get_message_demande()
    #     titre = "Au sujet de l'offre de " + produit.nom_produit


def contact_admins(request):
    if request.user.is_anonymous:
        form = ContactMailForm(request.POST or None, )
    else:
        form = ContactForm(request.POST or None, )

    if form.is_valid():

        if request.user.is_anonymous:
            envoyeur = "Anonyme : " + form.cleaned_data['email']
        else:
            envoyeur = request.user.username + " (" + request.user.email + ") "
        sujet = form.cleaned_data['sujet']
        message_txt = envoyeur + " a envoyé l'email suivant : "+ form.cleaned_data['msg']
        message_html = envoyeur + " a envoyé l'email' suivant : " + form.cleaned_data['msg']
        try:
            mail_admins(sujet, message_txt, html_message=message_html)
            if form.cleaned_data['renvoi']:
                if request.user.is_anonymous:
                    send_mail(sujet, "Vous avez envoyé aux administrateurs du site www.perma.cat le message suivant : " + message_html, form.cleaned_data['email'], [form.cleaned_data['email'],], fail_silently=False, html_message=message_html)
                else:
                    send_mail(sujet, "Vous avez envoyé aux administrateurs du site www.perma.cat le message suivant : " + message_html, request.user.email, [request.user.email,], fail_silently=False, html_message=message_html)

            return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                   'envoyeur': envoyeur ,
                                                   "destinataire": "administrateurs "})
        except BadHeaderError:
            return render(request, 'erreur.html', {'msg':'Invalid header found.'})

        return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})

    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":False})





def contact_admins2(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        if request.user.is_anonymous:
            envoyeur = "Anonyme"
        else:
            envoyeur = request.user.username + "(" + request.user.email + ") "
        sujet = form.cleaned_data['sujet']
        message = request.user.username + ' a envoyé le message suivant : \\n' + form.cleaned_data['message']
        mail_admins(sujet, message)
        if form.cleaned_data['renvoi'] :
            mess = "[Permacat] message envoyé aux administrateurs : \\n"
            send_mail( sujet, mess + message, request.user.email, [request.user.email,], fail_silently=False,)
        return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'message':message, 'envoyeur':request.user.username + "(" + request.uer.email + ")", "destinataire":"administrateurs d"
                                                                                                                                                                       "u site)"})
    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":False})


@login_required
def produitContacterProducteur(request, produit_id):
    prod = Produit.objects.get_subclass(pk=produit_id)
    receveur = prod.user
    form = ContactForm(request.POST or None)
    if form.is_valid():
        sujet =  "[Permacat] " + request.user.username + "(" + request.user.email+ ") vous contacte au sujet de: "  + form.cleaned_data['sujet']
        message = form.cleaned_data['message'] + '(par : ' + request.username + ')'

        send_mail( sujet, message, request.user.email, receveur.email, fail_silently=False,)
        if form.cleaned_data['renvoi'] :
            mess = "[Permacat] message envoyé à : "+receveur.email+"\\n"
            send_mail( sujet,mess + message, request.user.email, [request.user.email,], fail_silently=False,)

    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":True, "producteur":receveur.user.username})


@login_required
class profil_modifier_user(UpdateView):
    model = Profil
    form_class = ProducteurChangeForm
    template_name_suffix = '_modifier'
    fields = ['username', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences', 'pseudo_june', 'accepter_annuaire', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)


class profil_modifier_adresse(UpdateView):
    model = Adresse
    form_class = AdresseForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return self.request.user.adresse

    def post(self, request, **kwargs):
        self.object = self.get_object()
        self.object.save(recalc=True)
        return super(profil_modifier_adresse, self).post(request, **kwargs)

class profil_modifier(UpdateView):
    model = Profil
    form_class = ProducteurChangeForm
    template_name_suffix = '_modifier'
    #fields = ['username','email','first_name','last_name', 'site_web','description', 'competences', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

class profil_supprimer(DeleteAccess, DeleteView):
    model = Profil
    success_url = reverse_lazy('bienvenue')

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

@sensitive_variables('password')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_changer_form.html', {
        'form': form
    })

@sensitive_variables('user', 'password1', 'password2')
def register(request):
    if request.user.is_authenticated:
        return render(request, "erreur.html", {"msg":"Vous etes déjà inscrit.e et authentifié.e !"})
    
    form_adresse = AdresseForm(request.POST or None)
    form_profil = ProfilCreationForm(request.POST or None)
    if form_adresse.is_valid() and form_profil.is_valid():
        adresse = form_adresse.save()
        profil_courant = form_profil.save(commit=False,is_active = False)
        profil_courant.adresse = adresse
        #if profil_courant.statut_adhesion == 2:
        #    profil_courant.is_active=False
        profil_courant.save()
        Panier.objects.create(user=profil_courant)
        return render(request, 'userenattente.html')

    return render(request, 'register.html', {"form_adresse": form_adresse,"form_profil": form_profil,})


class ListeProduit(ListView):
    model = Produit
    context_object_name = "produits_list"
    template_name = "produit_list.html"
    paginate_by = 30

    def get_qs(self):
        qs = Produit.objects.select_subclasses()
        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__abreviation="public")
        else:
            for nomAsso in Choix.abreviationsAsso:
                if not getattr(self.request.user, "adherent_" + nomAsso):
                    qs = qs.exclude(asso__abreviation=nomAsso)

        params = dict(self.request.GET.items())

        if not "expire" in params:
            qs = qs.filter(Q(date_expiration__gt=date.today())| Q(date_expiration=None) )
        else:
            qs = qs.filter(Q(date_expiration__lt=date.today()) )

        
        if "distance" in params:
            listProducteurs = [p for p in Profil.objects.all() if p.getDistance(self.request.user) < float(params['distance'])] 
            qs = qs.filter(user__in=listProducteurs)

        if "producteur" in params:
            qs = qs.filter(user__username=params['producteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "souscategorie" in params:
            qs = qs.filter(Q(produit_aliment__souscategorie=params['souscategorie']) | Q(produit_vegetal__souscategorie=params['souscategorie']) | Q(produit_service__souscategorie=params['souscategorie'])  | Q(produit_objet__souscategorie=params['souscategorie']))

        if "prixmax" in params:
            qs = qs.filter(prix__lt=params['prixmax'])
        if "prixmin" in params:
            qs = qs.filter(prix__gtt=params['prixmin'])
        if "monnaie" in params:
            qs = qs.filter(unite_prix=params['monnaie'])
        if "gratuit" in params:
            qs = qs.filter(unite_prix='don')
        if "offre" in params:
            qs = qs.filter(estUneOffre=params['offre'])

        if "permacat" in params and self.request.user.adherent_pc:
            if params['permacat'] == "True":
                qs = qs.filter(estPublique=False)
            else:
                qs = qs.filter(estPublique=True)

        res = qs.order_by('-date_creation', 'categorie', 'user')
        if "ordre" in params:
            if params['ordre'] == 'categorie':
                res = qs.order_by('categorie', '-date_creation', 'user')
            elif params['ordre'] == "producteur" :
                res = qs.order_by('user', '-date_creation', 'categorie', )
            elif params['ordre'] == "date":
                res = qs.order_by('-date_creation', 'categorie', 'user', )

        return res

    def get_queryset(self):
        return self.get_qs()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('user__username', flat=True).distinct()
        context['choixPossibles'] = Choix.choix
        context['ordreTriPossibles'] = Choix.ordreTri
        context['distancePossibles'] = Choix.distances
        context['producteur_list'] = Profil.objects.all().order_by("username")
        context['typeFiltre'] = "aucun"
        # context['form'] = self.form
        if 'producteur' in self.request.GET:
            context['typeFiltre'] = "producteur"
        if 'souscategorie' in self.request.GET:
            categorie = get_categorie_from_subcat(self.request.GET['souscategorie'])
            context['categorie_parent'] = categorie
            context['typeFiltre'] = "souscategorie"
            context['souscategorie'] = self.request.GET['souscategorie']
        if 'categorie' in self.request.GET:
            context['categorie_parent'] = self.request.GET['categorie']
            context['typeFiltre'] = "categorie"
        context['typeOffre'] = '<- | ->'

        context['suivi'], created = Suivis.objects.get_or_create(nom_suivi="produits")
        return context

class ListeProduit_offres(ListeProduit):
    def get_queryset(self):
        qs = self.get_qs()
        qs = qs.filter(estUneOffre=True)
        return qs

    def get_context_data(self, **kwargs):
        context = ListeProduit.get_context_data(self, **kwargs)
        context['typeOffre'] = 'Offres->'
        return context

class ListeProduit_recherches(ListeProduit):
    def get_queryset(self):
        qs = self.get_qs()
        qs = qs.filter(estUneOffre=False)
        return qs

    def get_context_data(self, **kwargs):
        context = ListeProduit.get_context_data(self, **kwargs)
        context['typeOffre'] = '<-Demandes'
        return context

@login_required
def ajouterAuPanier(request, produit_id, quantite):#, **kwargs):
    quantite = float(quantite)
    produit = Produit.objects.get_subclass(pk=produit_id)
    # try:
    panier = Panier.objects.get(user=request.user, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    panier.add(produit, produit.unite_prix, quantite)
    return afficher_panier(request)

@login_required
def enlever_du_panier(request, item_id):
    panier = Panier.objects.get(user=request.user, etat="a")
    panier.remove_item(item_id)
    return afficher_panier(request)


@login_required
def afficher_panier(request):
    # try:
    panier = Panier.objects.get(user=request.user, etat="a")
    # panier = get_object_or_404(Panier, user__id=profil_id, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    items = Item.objects.order_by('produit__user').filter(panier__id=panier.id)
    return render(request, 'panier.html', {'panier':panier, 'items':items})


@login_required
def afficher_requetes(request):
    items = Item.objects.filter( produit__user__id =  request.user.id)
    return render(request, 'requetes.html', {'items':items})


@login_required
def chercher(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    if recherche:
        from blog.models import Commentaire, CommentaireProjet
        produits_list = Produit.objects.filter(Q(description__icontains=recherche) | Q(nom_produit__lower__contains=recherche), ).select_subclasses().distinct()
        articles_list = Article.objects.filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), ).distinct()
        projets_list = Projet.objects.filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), ).distinct()
        profils_list = Profil.objects.filter(Q(username__lower__contains=recherche)  | Q(description__icontains=recherche)| Q(competences__icontains=recherche), ).distinct()
        commentaires_list = Commentaire.objects.filter(Q(commentaire__icontains=recherche) ).distinct()
        commentairesProjet_list = CommentaireProjet.objects.filter(Q(commentaire__icontains=recherche)).distinct()
        salon_list = MessageGeneral.objects.filter(Q(message__icontains=recherche) ).distinct()
    else:
        produits_list = []
        articles_list = []
        projets_list = []
        profils_list = []
        commentaires_list, commentairesProjet_list, salon_list = [],[],[]

    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            produits_list = produits_list.exclude(asso__abreviation=nomAsso)
            articles_list = articles_list.exclude(asso__abreviation=nomAsso)
            projets_list = projets_list.exclude(asso__abreviation=nomAsso)

    return render(request, 'chercher.html', {'recherche':recherche, 'articles_list':articles_list, 'produits_list':produits_list, "projets_list": projets_list, 'profils_list':profils_list,'commentaires_list': commentaires_list, 'commentairesProjet_list':commentairesProjet_list, 'salon_list':salon_list})


@login_required
def chercher_articles(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    if recherche:
        from blog.models import Commentaire
        from jardinpartage.models import Article as ArticleJardin, Commentaire as CommJardin
        articles_list = Article.objects.filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), ).distinct()
        articles_jardin_list = ArticleJardin.objects.filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), ).distinct()
        commentaires_list = Commentaire.objects.filter(Q(commentaire__icontains=recherche) ).distinct()
        commentaires_jardin_list = CommJardin.objects.filter(Q(commentaire__icontains=recherche) ).distinct()
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                articles_list = articles_list.exclude(asso__abreviation=nomAsso)
                commentaires_list = commentaires_list.exclude(article__asso__abreviation=nomAsso)
    else:
        articles_list = []
        commentaires_list = []
        articles_jardin_list = []
        commentaires_jardin_list = []


    return render(request, 'chercherForum.html', {'recherche':recherche, 'articles_list':articles_list, 'articles_jardin_list':articles_jardin_list, 'commentaires_jardin_list':commentaires_jardin_list,'commentaires_list': commentaires_list})


@login_required
def lireConversation(request, destinataire):
    conversation = getOrCreateConversation(request.user.username, destinataire)
    messages = Message.objects.filter(conversation=conversation).order_by("date_creation")

    message_defaut = None
    id_panier = request.GET.get('panier')
    if id_panier:
        id_destinataire = Profil.objects.get(username=destinataire).id
        message_defaut = Panier.objects.get(id=id_panier).get_message_demande(int(id_destinataire))

    id_produit = request.GET.get('produit')
    if id_produit:
        message_defaut = Produit.objects.get(id=id_produit).get_message_demande()

    form = MessageForm(request.POST or None, message=message_defaut)
    if form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        message.auteur = request.user
        conversation.date_dernierMessage = message.date_creation
        conversation.dernierMessage =  ("(" + str(message.auteur) + ") " + str(strip_tags(message.message).replace('&nspb',' ')))[:96]
        if len("(" + str(message.auteur) + ") " + str(strip_tags(message.message).replace('&nspb',' '))) > 96:
            conversation.dernierMessage += "..."
        conversation.save()
        message.save()
        url = conversation.get_absolute_url()
        action.send(request.user, verb='envoi_salon_prive', action_object=conversation, url=url, group=destinataire,
                    description="a envoyé un message privé à " + destinataire)
        profil_destinataire = Profil.objects.get(username=destinataire)
        suivi, created = Suivis.objects.get_or_create(nom_suivi='conversations')
        if profil_destinataire in followers(suivi):
            titre = "Message Privé"
            message = request.user.username + " vous a envoyé un <a href='https://www.perma.cat"+  url+"'>" + "message</a>"
            emails = [profil_destinataire.email, ]
            action.send(request.user, verb='emails', url=url, titre=titre, message=message, emails=emails)

            # try:
            #     send_mail(sujet, message, SERVER_EMAIL, [profil_destinataire.email, ], fail_silently=False,)
            # except Exception as inst:
            #     mail_admins("erreur mails",
            #             sujet + "\n" + message + "\n xxx \n" + str(profil_destinataire.email) + "\n erreur : " + str(inst))
        return redirect(request.path)

    return render(request, 'lireConversation.html', {'conversation': conversation, 'form': form, 'messages_echanges': messages, 'destinataire':destinataire})



@login_required
def lireConversation_2noms(request, destinataire1, destinataire2):
    if request.user.username==destinataire1:
        return lireConversation(request, destinataire2)
    elif request.user.username==destinataire2:
        return lireConversation(request, destinataire1)
    else:
        return render(request, 'erreur.html', {'msg':"Vous n'êtes pas autorisé à voir cette conversation"})

class ListeConversations(ListView):
    model = Conversation
    context_object_name = "conversation_list"
    template_name = "conversations.html"
    paginate_by = 1

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['conversations'] = Conversation.objects.filter(Q(profil2__id=self.request.user.id) | Q(profil1__id=self.request.user.id)).order_by('-date_dernierMessage')
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="conversations")

        return context

def chercherConversation(request):
    form = ChercherConversationForm(request.user, request.POST or None,)
    if form.is_valid():
        destinataire = (Profil.objects.all().order_by('username'))[int(form.cleaned_data['destinataire'])]
        return redirect('agora_conversation', destinataire=destinataire)
    else:
        return render(request, 'chercher_conversation.html', {'form': form})


@login_required
def getNbProduits_expires(request):
    return len(Produit.objects.filter(user=request.user, date_expiration__lt=date.today()))


@login_required
def supprimerProduits_expires_confirmation(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")

    qs = Produit.objects.select_subclasses()
    produits = qs.filter(user=request.user, date_expiration__lt=date.today())
    return render(request, 'bourseLibre/produitexpires_confirm_delete.html', {'produits': produits,})

@login_required
def supprimerProduits_expires(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")
    produits = Produit.objects.filter(user=request.user, date_expiration__lt=date.today())

    for prod in produits:
        prod.delete()

    return redirect('bienvenue')


@login_required
def prochaines_rencontres(request):
    return render(request, 'notifications/prochaines_rencontres.html', {})



@login_required
def mesSuivis(request):

    follows = Follow.objects.filter(user=request.user)
    follows_base, follows_agora, follows_autres, follows_forum = [], [], [], []
    for action in follows:
        if not action.follow_object:
            action.delete()
        elif 'articles' in str(action.follow_object) and not str(action.follow_object) == "articles_jardin":
            follows_forum.append(action)
        elif 'agora' in str(action.follow_object):
            follows_agora.append(action)
        elif str(action.follow_object) in Choix.suivisPossibles:
            follows_base.append(action)
        else:
            follows_autres.append(action)

    return render(request, 'notifications/mesSuivis.html', {'follows_base': follows_base, 'follows_agora':follows_agora, 'follows_forum':follows_forum, 'follows_autres':follows_autres})

@login_required
def supprimerAction(request, actionid):
    try:
        action = Follow.objects.get(id=actionid)
        action.delete()
    except:
        messages.info(request, 'Abonnement introuvable, désolé')

    return redirect('mesSuivis')


@login_required
def mesActions(request):
    return render(request, 'notifications/mesActions.html', {})



@login_required
def agora(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    suivis, created = Suivis.objects.get_or_create(nom_suivi="agora_" + str(asso.abreviation))
    messages = MessageGeneral.objects.filter(asso__abreviation=asso.abreviation).order_by("date_creation")
    form = MessageGeneralForm(request.POST or None) 
    if form.is_valid(): 
        message = form.save(commit=False) 
        message.auteur = request.user 
        message.asso = asso
        message.save()
        group, created = Group.objects.get_or_create(name='tous')
        url = reverse('agora', kwargs={'asso':asso.abreviation})
        action.send(request.user, verb='envoi_salon_'+str(asso.abreviation), action_object=message, target=group, url=url, description="a envoyé un message dans le salon " + str(asso.nom))

        return redirect(request.path)
    return render(request, 'agora.html', {'form': form, 'messages_echanges': messages, 'asso':asso, 'suivis':suivis})

# class ServiceWorkerView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'fcmtest/firebase-messaging-sw.js', content_type="application/x-javascript")
#
# @require_POST
# @csrf_exempt
# def send_push(request):
#     try:
#         body = request.body
#         data = json.loads(body)
#
#         if 'head' not in data or 'body' not in data or 'id' not in data:
#             return JsonResponse(status=400, data={"message": "Invalid data format"})
#
#         user_id = data['id']
#         user = get_object_or_404(User, pk=user_id)
#         payload = {'head': data['head'], 'body': data['body']}
#         send_user_notification(user=user, payload=payload, ttl=1000)
#
#         return JsonResponse(status=200, data={"message": "Web push successful"})
#     except TypeError:
#         return JsonResponse(status=500, data={"message": "An error occurred"})


@login_required
@csrf_exempt
def suivre_conversations(request, actor_only=True):
    """
    """
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'conversations')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('conversations')

@login_required
@csrf_exempt
def suivre_produits(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'produits')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('marche')


@login_required
def sereabonner(request,):
    for suiv in Choix.suivisPossibles:
        suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)

        if not suivi in following(request.user):
            actions.follow(request.user, suivi, send_action=False)

    for abreviation in Choix.abreviationsAsso + ['public']:
        if request.user.est_autorise(abreviation):
            suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_" + abreviation)
            actions.follow(request.user, suivi, send_action=False)
            suivi, created = Suivis.objects.get_or_create(nom_suivi="agora_" + abreviation)
            actions.follow(request.user, suivi, send_action=False)

    return redirect('mesSuivis')


def inscription_newsletter(request):
    form = InscriptionNewsletterForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.save()
        return render(request, 'merci.html', {'msg' :"Vous êtes inscrits à la newsletter"})
    return render(request, 'registration/inscription_newsletter.html', {'form':form})


@login_required
def inscription_permagora(request):
    asso=Asso.objects.get(abreviation='scic')
    if request.user.adherent_scic:
        request.user.adherent_scic = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_scic')
        actions.unfollow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': 'scic'})
        action.send(request.user, verb='inscription_permagora', target=asso, url=url,
                    description="s'est retiré du groupe PermAgora")
    else:
        request.user.adherent_scic = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_scic')
        actions.follow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': 'scic'})
        action.send(request.user, verb='inscription_permagora', target=asso, url=url,
                    description="s'est inscrit.e au groupe PermAgora")
    return redirect('presentation_asso', asso='scic')


@login_required
def inscription_citealt(request):
    asso=Asso.objects.get(abreviation='citealt')
    if request.user.adherent_citealt:
        request.user.adherent_citealt = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_citealt')
        actions.unfollow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': 'citealt'})
        action.send(request.user, verb='inscription_citealt', target=asso, url=url,
                    description="s'est retiré du groupe Cité Altruiste")
    else:
        request.user.adherent_citealt = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_citealt')
        actions.follow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': 'citealt'})
        action.send(request.user, verb='inscription_citealt', target=asso, url=url,
                    description="s'est inscrit.e dans le groupe Cité Altruiste")
    return redirect('presentation_asso', asso='citealt')


@login_required
def contacter_newsletter(request):
    if not request.user.adherent_pc:
        return render(request, "notPermacat.html")

    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[permacat] Newsletter - " +  form.cleaned_data['sujet']
            message = form.cleaned_data['msg']
            emails = [profil.email for profil in Profil.objects.filter(inscrit_newsletter=True)] + [profil.email for
                                                                                                    profil in
                                                                                                    InscriptionNewsletter.objects.all()]
            if emails and not LOCALL:
                try:
                    send_mass_mail([(sujet, message, SERVER_EMAIL, emails), ])
                except:
                    sujet = "[permacat admin] Erreur lors de l'envoi du mail"
                    message_txt = message + '\n'.join(emails)

                    try:
                        mail_admins(sujet, message_txt)
                    except:
                        print("erreur de la fonction contacterNewsletter (views.py)")
                        pass
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg': message,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataires": emails})
    else:
        form = ContactForm()
    return render(request, 'contact/contact_newsletter.html', {'form': form, })



@login_required
def contacter_adherents(request):
    if not request.user.adherent_pc:
        return render(request, "notPermacat.html")

    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[permacat] Newsletter - " +  form.cleaned_data['sujet']
            message = form.cleaned_data['msg']
            emails = [profil.email for profil in Profil.objects.filter(adherent_pc=True)]

            if emails and not LOCALL:
                try:
                    send_mass_mail([(sujet, message, SERVER_EMAIL, emails), ])
                except:
                    sujet = "[permacat admin] Erreur lors de l'envoi du mail"
                    message_txt = message + '\n'.join(emails)

                    try:
                        mail_admins(sujet, message_txt)
                    except:
                        print("erreur de la fonction contacterAdherents (views.py)")
                        pass
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg': message,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataires": emails})
    else:
        form = ContactForm()
    return render(request, 'contact/contact_adherents.html', {'form': form, })



@login_required
def modifier_message(request, id, type_msg, asso, ):
    if type_msg == 'conversation':
        obj = Message.objects.get(id=id)
        conversation = obj.conversation
    else:
        asso = testIsMembreAsso(request, asso)
        if not isinstance(asso, Asso):
            raise PermissionDenied
        obj = MessageGeneral.objects.get(id=id, asso=asso)

    form = MessageChangeForm(request.POST or None, instance=obj)

    if form.is_valid():
        object = form.save()
        if object.message and object.message !='<br>'and object.message !='<p><br></p>':
            object.date_modification = now()
            object.save()
            return redirect(object.get_absolute_url())
        else:
            object.delete()
            if type_msg == 'conversation':
                return redirect(conversation.get_absolute_url())
            else:
                return reverse('agora', kwargs={asso:asso.abreviation})



    return render(request, 'modifierCommentaire.html', {'form': form, })


@login_required
@csrf_exempt
def suivre_agora(request, asso, actor_only=True):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied

    suivi, created = Suivis.objects.get_or_create(nom_suivi='agora_' + str(asso.abreviation))

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('agora', asso=asso.abreviation)


@login_required
def accesfichier(request, path):
    response = HttpResponse()
    # Content-type will be detected by nginx
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected/media/' + path
    return response