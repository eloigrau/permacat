# -*- coding: utf-8 -*-
'''
Created on 25 mai 2017

@author: tchenrezi
'''
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect  # render_to_response,
from .forms import Produit_aliment_CreationForm, Produit_vegetal_CreationForm, Produit_objet_CreationForm, \
    Produit_service_CreationForm, ProducteurCreationForm, ContactForm, AdresseForm, ProfilCreationForm
from .models import Profil, Produit, Adresse, Choix, Panier, Item, get_categorie_from_subcat#, ProductFilter#, Produit_aliment, Produit_service, Produit_objet, Produit_vegetal
# from django.db.models import Q
from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import mail_admins, send_mail
# from itertools import chain
from django.db.models import Q

from django import forms

from blog.models import Article
from django.core.exceptions import ObjectDoesNotExist

import sys
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
#from braces.views import LoginRequiredMixin


def bienvenue(request):
    return render(request, 'bienvenue.html')

def presentation_asso(request):
    return render(request, 'presentation_asso.html')

def statuts(request):
    return render(request, 'statuts.html')


@login_required(login_url='/login/')
def produit_proposer(request, typeProduit):
    try:
        bgcolor = Choix.couleurs[typeProduit]
    except:
        bgcolor = None

    if typeProduit == 'aliment':
        type_form = Produit_aliment_CreationForm(request.POST or None, request.FILES or None)
    elif typeProduit == 'vegetal':
        type_form = Produit_vegetal_CreationForm(request.POST or None, request.FILES or None)
    elif typeProduit == 'service':
        type_form = Produit_service_CreationForm(request.POST or None, request.FILES or None)
    elif typeProduit == 'objet':
        type_form = Produit_objet_CreationForm(request.POST or None, request.FILES or None)
    else:
        raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')
    if  type_form.is_valid():
       # produit = produit_form.save(commit=False)
        produit = type_form.save(commit=False)
        produit.user = Profil.objects.get(pk=request.user.id)
        produit.categorie = typeProduit

        #if produit.photo:
            #produit.photo = request.FILES['photo']
            #file_type = produit.photo.url.split('.')[-1].lower()

            #if file_type not in IMAGE_FILE_TYPES:
            #    context = {
            #        'produit': produit, 'form': produit,
            #        'error_message': 'Image file must be PNG, JPG, or JPEG',
            #    }
            #    return render(request, 'bourseLibre/produit_proposer.html', context)

            # #Opening the uploaded image
            # im = Image.open(produit.photo)
            #
            # output = BytesIO()
            #
            # #Resize/modify the image
            # im = im.resize( (100,100) )
            #
            # #after modifications, save it to the output
            # im.save(output, format='JPEG', quality=100)
            # output.seek(0)
            #
            # #change the imagefield value to be the newley modifed image value
            # produit.photo = InMemoryUploadedFile(output,'ImageField', "%s.jpg" % produit.photo.url.split('.')[0], 'images', sys.getsizeof(output), None)

        produit.save()
        # type = type_form.save(commit=False)
        # type.proprietes = produit
        # type.save()
        return HttpResponseRedirect('/produits/detail/' + str(produit.id))
    return render(request, 'bourseLibre/produit_proposer.html', {"form": type_form, "bgcolor": bgcolor, "typeProduit":typeProduit})


# @login_required(login_url='/login/')
class ProduitModifier(UpdateView):
    model = Produit
    template_name_suffix = '_modifier'
    fields = ['date_debut','date_expiration','nom_produit', 'description', 'prix', 'unite_prix', 'categorie', 'photo', 'estUneOffre',]# 'souscategorie','etat','type_prix']

    widgets = {
        'date_debut': forms.DateInput(attrs={'type': "date"}),
        'date_expiration': forms.DateInput(attrs={'type': "date"})
    }
    # field

    def get_form_class(self):
        if self.object.categorie == 'aliment':
            return Produit_aliment_CreationForm
        elif self.object.categorie == 'vegetal':
            return Produit_vegetal_CreationForm
        elif self.object.categorie == 'service':
            return Produit_service_CreationForm
        elif self.object.categorie == 'objet':
            return Produit_objet_CreationForm
        else:
            raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')
        return get_produitForm(self.request, self.object.categorie)



# @login_required(login_url='/login/')
class ProduitSupprimer(DeleteView):
    model = Produit
    success_url = reverse_lazy('produit_lister')

@login_required(login_url='/login/')
def proposerProduit_entree(request):
    return render(request, 'bourseLibre/produit_proposer_entree.html', {"couleurs":Choix.couleurs})


# @login_required
# def supprimerProduit(request, produit_id):
#     produit = Produit.objects.get(pk=produit_id)
#     produit.delete()
#     produit = Produit.objects.filter(user=request.user)
#     return render(request, 'indexProduits.html', {'produit': produit})

@login_required
def detailProduit(request, produit_id):
    prod = Produit.objects.get_subclass(pk=produit_id)
    return render(request, 'bourseLibre/produit_detail.html', {'produit': prod})


def merci(request, template_name='merci.html'):
    return render(request, template_name)


# @login_required
# def index(request):
#         produits = Produit.objects.filter(user=request.user)
#         query = request.GET.get("q")
#         if query:
#             produits = produits.filter(
#                 Q(album_title__icontains=query) | 
#                 Q(artist__icontains=query)
#             ).distinct()
#             return render(request, 'index.html', {
#                 'produits': produits,
#             })
#         else:
#             return render(request, 'index.html', {'produits': produits})

# @login_required(login_url='/login/')
def profil_courant(request, ):
    user = get_object_or_404(User, id=request.user.id)
    return render(request, 'profil.html', {'user': user})


# @login_required(login_url='/login/')
def profil(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        return render(request, 'profil.html', {'user': user})
    except User.DoesNotExist:
        # try:
        #     user = User.objects.get(username=kwargs['user_username'])
        #     return render(request, 'profil.html', {'user': user})
        # except User.DoesNotExist:
            return render(request, 'profil_inconnu.html', {'userid': user_id})

# @login_required(login_url='/login/')
def profil_nom(request, user_username):
    try:
        user = User.objects.get(username=user_username)
        return render(request, 'profil.html', {'user': user})
    except User.DoesNotExist:
        return render(request, 'profil_inconnu.html', {'userid': user_username})

# @login_required(login_url='/login/')
def profil_inconnu(request):
    return render(request, 'profil_inconnu.html')

# @login_required(login_url='/login/')
def profil_list(request):
    profils = Profil.objects.all()
    return render(request, 'cooperateurs.html', {'profils':profils, } )

# @login_required(login_url='/login/')
def profil_carte(request):
    profils = Profil.objects.all()
    return render(request, 'carte_cooperateurs.html', {'profils':profils, } )

# @login_required(login_url='/login/')
def profil_contact(request, user_id):
    message = None
    titre = None
    id_panier = request.GET.get('panier')
    if id_panier:
        panier = Panier.objects.get(id=id_panier)
        message = panier.get_message_demande(int(user_id))
        titre = "Proposition d'échange"

    id_produit = request.GET.get('produit')
    if id_produit:
        produit = Produit.objects.get(id=id_produit)
        message = produit.get_message_demande()
        titre = "Au sujet de l'offre de " + produit.nom_produit

    form = ContactForm(request.POST or None, message=message, titre=titre)
    recepteur = Profil.objects.get(id=user_id)
    if form.is_valid():
        sujet = request.user.username +'vous a écrit:', form.cleaned_data['sujet']
        message = form.cleaned_data['message']
        send_mail(
            sujet,
            message,
            request.user.email,
            recepteur.user.email,
            fail_silently=False,
            )
        return render(request, 'message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'message':message, 'envoyeur':request.user.username + "(" + request.user.email + ")", "destinataire":recepteur.user.username + "(" +recepteur.user.email+ ")"})
        # if renvoi:
        #     mess = "message envoyé a la bourse libre : \\n"
        #     send_mail( sujet,mess + message, envoyeur, to=[envoyeur], fail_silently=False,)
    return render(request, 'profil_contact.html', {'form': form, 'recepteur':recepteur})


def contact_admins(request):
    form = ContactForm(request.POST or None, envoyeur=request.user.email)
    if form.is_valid():
        sujet = form.cleaned_data['sujet']
        message = request.user.username + ' a envoyé le message suivant : \\n' + form.cleaned_data['message']
        mail_admins(sujet, message)
        if form.cleaned_data['renvoi'] :
            mess = "[MarchéLibre] message envoyé aux administrateurs : \\n"
            send_mail( sujet,mess + message, request.user.email, request.user.email, fail_silently=False,)

        #         try:
        #             f.save()
        #             print("success")
        #             messages.add_message(request, messages.SUCCESS, 'Feedback sent!')
        #         except:
        #             print("failed")
        #             messages.add_message(request, messages.INFO, 'Unable to send feedback. Try agian')

        #         send_mail( sujet,message, envoyeur, to=['labourselibre@gmail.com'], fail_silently=False,)
        #         if renvoi:
        #             mess = "message envoyé a la bourse libre : \\n"
        #             send_mail( sujet,mess + message, envoyeur, to=[envoyeur], fail_silently=False,)

    return render(request, 'contact.html', {'form': form, "isContactProducteur":False})


# @login_required(login_url='/login/')
def produitContacterProducteur(request, produit_id):
    prod = Produit.objects.get_subclass(pk=produit_id)
    receveur = prod.user
    form = ContactForm(request.POST or None, envoyeur=request.user.email)
    if form.is_valid():
        sujet =  "[MarchéLibre]" + form.cleaned_data['sujet']
        message = form.cleaned_data['message'] + '(par : ' + request.user.username + ')'

        send_mail( sujet, message, request.user.email, receveur.email, fail_silently=False,)
        if form.cleaned_data['renvoi'] :
            mess = "[MarchéLibre] message envoyé à : \\n"
            send_mail( sujet,mess + message, request.user.email, request.user.email, fail_silently=False,)

    return render(request, 'contact.html', {'form': form, "isContactProducteur":True, "producteur":receveur.user.username})


# @login_required(login_url='/login/')
class profil_modifier_user(UpdateView):
    model = Profil
    form_class = ProducteurCreationForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return User.objects.get(id=self.request.user.id)

# @login_required(login_url='/login/')
class profil_modifier_adresse(UpdateView):
    model = Adresse
    form_class = AdresseForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Adresse.objects.get(id=self.request.user.id)

# @login_required(login_url='/login/')
class profil_modifier(UpdateView):
    model = Profil
    form_class = ProfilCreationForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

# @login_required(login_url='/login/')
def register(request):
    form_adresse = AdresseForm(request.POST or None)
    #form_user = UserCreationForm(request.POST or None)
    form_user = ProducteurCreationForm(request.POST or None)
    form_profil = ProfilCreationForm(request.POST or None)
    if form_adresse.is_valid() and form_user.is_valid() and form_profil.is_valid():
        user = form_user.save(commit=True,is_active = False)
        adresse = form_adresse.save()
        profil_courant = form_profil.save(commit=False)
        profil_courant.user = user
        profil_courant.adresse = adresse
        profil_courant.save()
        Panier.objects.create(user=profil_courant)
        return render(request, 'userenattente.html')

    return render(request, 'register.html', {"form_adresse": form_adresse,"form_user": form_user,"form_profil": form_profil,})


from django.views.generic.edit import ModelFormMixin



# @login_required(login_url='/login/')
class ListeProduit(ListView):
    model = Produit
    context_object_name = "produits_list"
    template_name = "produit_list.html"
    paginate_by = 21

    def get_qs(self):
        qs = Produit.objects.select_subclasses()
        params = dict(self.request.GET.items())

        if "producteur" in params:
            qs = qs.filter(user__user__username=params['producteur'])
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

        res = qs.order_by('date_creation', 'categorie', 'user')
        if "ordre" in params:
            if params['ordre'] == 'categorie':
                res = qs.order_by('categorie', 'date_creation', 'user')
            elif params['ordre'] == "producteur" :
                res = qs.order_by('user', 'date_creation', 'categorie', )
            elif params['ordre'] == "date":
                res = qs.order_by('date_creation', 'categorie', 'user', )

        return res

    def get_queryset(self):
        return self.get_qs()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('user__username', flat=True).distinct()
        context['choixPossibles'] = Choix.choix
        context['ordreTriPossible'] = Choix.ordreTri
        context['producteur_list'] = Profil.objects.all()
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

def charte(request):
    return render(request, 'charte.html', )

def cgu(request):
    return render(request, 'cgu.html', )

# @login_required(login_url='/login/')
def liens(request):
    liens = [
        'https://www.monnaielibreoccitanie.org/',
        'https://www.colibris-lemouvement.org/',
        'https://framasoft.org',
        'http://www.le-message.org/?lang=fr',
        'https://reporterre.net/',
        'https://www.helloasso.com/associations/mlcpo/collectes/soudaqui-la-monnaie-locale-des-p-o-c-est-maintenant',
        'https://la-bas.org/',
        'https://colibris-universite.org/mooc-permaculture/wakka.php?wiki=PagePrincipale',
    ]
    return render(request, 'liens.html', {'liens':liens})

def fairedon(request):
    return render(request, 'fairedon.html', )



# @login_required(login_url='/login/')
def ajouterAuPanier(request, produit_id, quantite):#, **kwargs):
    quantite = float(quantite)
    produit = Produit.objects.get_subclass(pk=produit_id)
    profil = Profil.objects.get(user__id=request.user.id)
    # try:
    panier = Panier.objects.get(user=profil, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    panier.add(produit, produit.unite_prix, quantite)
    return afficher_panier(request)

# @login_required(login_url='/login/')
def enlever_du_panier(request, item_id):
    profil = Profil.objects.get(user__id=request.user.id)
    panier = Panier.objects.get(user=profil, etat="a")
    panier.remove_item(item_id)
    return afficher_panier(request)


# @login_required(login_url='/login/')
def afficher_panier(request):
    # try:
    profil = Profil.objects.get(user__id=request.user.id)
    panier = Panier.objects.get(user=profil, etat="a")
    # panier = get_object_or_404(Panier, user__id=profil_id, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    items = Item.objects.order_by('produit__user').filter(panier__id=panier.id)
    return render(request, 'panier.html', {'panier':panier, 'items':items})


# @login_required(login_url='/login/')
def afficher_requetes(request):
    items = Item.objects.filter( produit__user__id =  request.user.id)
    return render(request, 'requetes.html', {'items':items})


# @login_required(login_url='/login/')
def chercher(request):
    recherche = request.GET.get('id_recherche')
    if recherche:
        produits_list = Produit.objects.filter(Q(description__contains=recherche) | Q(nom_produit__contains=recherche), ).select_subclasses()
        articles_list = Article.objects.filter(Q(titre__contains=recherche) | Q(contenu__contains=recherche), )
        profils_list = Profil.objects.filter(Q(user__username__contains=recherche)  | Q(description__contains=recherche)| Q(competences__contains=recherche), )
    else:
        produits_list = []
        articles_list = []
        profils_list = []
    return render(request, 'chercher.html', {'recherche':recherche, 'articles_list':articles_list, 'produits_list':produits_list, 'profils_list':profils_list})


# from django_filters import rest_framework as filters
# from rest_framework import generics
# from .models import ProduitSerializer
#
# class ProductList(generics.ListAPIView):
#     queryset = Produit.objects.all().select_subclasses()
#     filter_backends = (filters.DjangoFilterBackend,)
#     serializer_class = ProduitSerializer
#
# def product_list(request):
#     f = ProductFilter(request.GET, queryset=Produit.objects.all().select_subclasses())
#     return render(request, 'templateList.html', {'filter': f})

    # res = [Produit_aliment.objects.all(), Produit_vegetal.objects.all(), Produit_service.objects.all(), Produit_objet.objects.all()]
    # queryset = list(chain(*res))
    #queryset = qs=[Produit_aliment.objects.all(), Produit_vegetal.objects.all(), Produit_service.objects.all(), Produit_objet.objects.all())


    # def get_queryset(self):
    #     filter_val = self.request.GET.get('filter', 'give-default-value')
    #     order = self.request.GET.get('orderby', 'give-default-value')
    #     new_context = Update.objects.filter(
    #         state=filter_val,
    #     ).order_by(order)
    #     return new_context

    #
    # def get_context_data(self, **kwargs):
    #     context = super(MyView, self).get_context_data(**kwargs)
    #     context['filter'] = self.request.GET.get('filter', 'give-default-value')
    #     context['orderby'] = self.request.GET.get('orderby', 'give-default-value')
    #     return context

# class ListeProduitFiltre(ListView):
#     model = Produit
#     context_object_name = "produits_list"
#     template_name = "produit_list.html"
#     paginate_by = 18
#
#     def get_queryset(self):
#         qs = Produit.objects.select_subclasses()
#         params = dict(self.request.GET.items())
#         if "filtrer_producteur" in params:
#             qs = qs.filter(user__user__username=self.request.GET.get('filtrer_producteur') )
#
#         if "categorie" in self.kwargs:
#            # return list(chain(*([Produit_aliment.objects.filter(proprietes__categorie=self.kwargs["categorie"]), Produit_vegetal.objects.filter(proprietes__categorie=self.kwargs["categorie"]), Produit_service.objects.filter(proprietes__categorie=self.kwargs["categorie"]), Produit_objet.objects.filter(proprietes__categorie=self.kwargs["categorie"])])))
#             return qs.filter(categorie=self.kwargs["categorie"]).select_subclasses()
#         elif "producteur" in self.kwargs:
#            # return list(chain(*([Produit_aliment.objects.filter(proprietes__user__user__username=self.kwargs["producteur"]), Produit_vegetal.objects.filter(proprietes__user__user__username=self.kwargs["producteur"]), Produit_service.objects.filter(proprietes__user__user__username=self.kwargs["producteur"]), Produit_objet.objects.filter(proprietes__user__user__username=self.kwargs["producteur"])])))
#             return qs.filter(user__user__username=self.kwargs["producteur"]).select_subclasses()
#         else:
#             return qs
#             #return list(chain(*([Produit_aliment.objects.all(), Produit_vegetal.objects.all(), Produit_service.objects.all(), Produit_objet.objects.all()])))
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the publisher
#         if "categorie" in self.kwargs:
#             context['typeFiltre'] = "categorie"
#             context['filtre'] = self.kwargs["categorie"]
#         elif "producteur" in self.kwargs:
#             context['typeFiltre'] = "producteur"
#             context['filtre'] = self.kwargs['producteur']
#         return context
#
#
# class ListeProduitCategorie(ListView):
#     model = Produit
#     context_object_name = "produits_list"
#     template_name = "produit_list.html"
#     paginate_by = 18
#
#     def get_queryset(self):
#         return Produit.objects.filter(categorie=self.kwargs["categorie"])
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the publisher
#         context['typeFiltre'] = "categorie"
#         context['filtre'] = self.kwargs["categorie"]
#         print(context)
#         return context
#
# class ListeProduitProducteur(ListView):
#     model = Produit
#     context_object_name = "produits_list"
#     template_name = "produit_list.html"
#     paginate_by = 18
#
#     def get_queryset(self):
#         return Produit.objects.filter(user__username=self.kwargs["producteur"])
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in the publisher
#         context['typeFiltre'] = "producteur"
#         context['filtre'] = context['user.username']
#         return context


