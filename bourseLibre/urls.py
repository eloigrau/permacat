# -*- coding: utf-8 -*-
"""bourseLibre URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog__ import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog__/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.urls import path

from . import views

# On import les vues de Django, avec un nom spécifique
#from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

# admin.autodiscover()
from django.contrib import admin
# from django_filters.views import FilterView
# from .models import Produit, ProductFilter

urlpatterns = [
    url(r'^$', views.bienvenue, name='bienvenue'),
    url(r'^permacat/presentation$', views.presentation_asso, name='presentation_asso'),
    url(r'^permacat/statuts$$', views.statuts, name='statuts'),
    
    url(r'^admin/', admin.site.urls, name='admin'),
    #path('admin/', admin.site.urls, name='admin'),
    url(r'^merci/$', views.merci, name='merci'),
    url(r'^blog/', include('blog.urls', namespace='bourseLibre.blog')),
    # url(r'^search/', include('haystack.urls'), name='chercher_site'),
    #url(r'^search/', include('haystack.urls'), name='haystack_search'),
    url(r'^chercher/produit/$', login_required(views.chercher, login_url='/auth/login/'), name='chercher'),
    url(r'^accounts/profil/(?P<user_id>[0-9]+)/$', views.profil, name='profil',),
    url(r'^accounts/profil/(?P<user_username>[-A-Za-z]+)/$', views.profil_nom, name='profil_nom',),
    #url(r'^accounts/profile/(<user_id>[a-zA-Z0-9.]+)', views.profil, name='profil',),
    url(r'^accounts/profile/$', views.profil_courant, name='profil_courant',),
    url(r'^accounts/profil_inconnu/$', views.profil_inconnu, name='profil_inconnu',),
    url(r'^accounts/profil_modifier/$', login_required(views.profil_modifier.as_view(), login_url='/auth/login/'), name='profil_modifier',),
    url(r'^accounts/profil_modifier_user/$', login_required(views.profil_modifier_user.as_view(), login_url='/auth/login/'), name='profil_modifier_user',),
    url(r'^accounts/profil_modifier_adresse/$', login_required(views.profil_modifier_adresse.as_view(), login_url='/auth/login/'), name='profil_modifier_adresse',),
    #url(r'^accounts/profil_contact/(?P<user_id>[0-9]+)$', views.profil_contact, name='profil_contact'),
    #url(r'^accounts/profil_contact/(?P<user_id>[0-9]+)/(?P<message>D+)$', views.profil_contact, name='profil_contact'),
    url(r'^accounts/profil_contact/(?P<user_id>[0-9]+)/$', views.profil_contact, name='profil_contact',),
    url(r'^register/$', views.register, name='senregistrer',),
    path('auth/', include('django.contrib.auth.urls')),
    #url(r'^login/$', views.login, {'template_name': 'login.html'},  name='login_user', ),
    #url( r'^login/$',auth_views.LoginView.as_view(template_name="login.html"), name="login_user"),
    #url(r'^passwordchange/$', auth_views.password_change, name='password_change',),

    url(r'^contact_admins/$', views.contact_admins, name='contact_admins',),
    url(r'^charte/$', views.charte, name='charte',),
    url(r'^cgu/$', views.cgu, name='cgu',),
    url(r'^liens/$', views.liens, name='liens',),
    url(r'^fairedon/$', views.fairedon, name='fairedon',),
    url(r'^cooperateurs/$', login_required(views.profil_list, login_url='/auth/login/'), name='profil_list',),
    url(r'^cooperateurs/carte/$', login_required(views.profil_carte, login_url='/auth/login/'), name='profil_carte',),

    url(r'^produits/proposer/(?P<typeProduit>[-A-Za-z]+)/$', login_required(views.produit_proposer, login_url='/auth/login/'), name='produit_proposer', ),
    url(r'^produits/proposer/', login_required(views.proposerProduit_entree, login_url='/auth/login/'), name='produit_proposer_entree',),
    #url(r'^shop/', include(shop_urls)), # <-- That's the important bit

    # url(r'^list$', views.product_list),
    #     url(r'^list2/$', FilterView.as_view(model=Produit, filterset_class=ProductFilter,)),
    url(r'^produits/lister/', login_required(views.ListeProduit.as_view(), login_url='/auth/login/'),
        name="produit_lister"),
    url(r'^produits/lister_offres/', login_required(views.ListeProduit_offres.as_view(), login_url='/auth/login/'),
        name="produit_lister_offres"),
    url(r'^produits/lister_recherches/', login_required(views.ListeProduit_recherches.as_view(), login_url='/auth/login/'),
        name="produit_lister_recherches"),

    url(r'^produits/detail/(?P<produit_id>[0-9]+)/$', views.detailProduit, name='produit_detail',),

    url(r'^produits/modifier/(?P<pk>[0-9]+)/$',
        login_required(views.ProduitModifier.as_view(), login_url='/auth/login/'), name='produit_modifier', ),
    # url(r'^produits/ajouter/(?P<pk>[0-9]+)/$',
    #     login_required(views.ProduitModifier.as_view(), login_url='/auth/login/'), name='produit_ajouterAuPanier', ),
    url(r'^produits/contacterProducteur/(?P<producteur_id>[0-9]+)/$',
        login_required(views.produitContacterProducteur, login_url='/auth/login/'), name='produit_contacterProducteur', ),
    url(r'^produits/supprimer/(?P<pk>[0-9]+)/$',
        login_required(views.ProduitSupprimer.as_view(), login_url='/auth/login/'), name='produit_supprimer', ),

    url(r'^panier/afficher/$',
        login_required(views.afficher_panier, login_url='/auth/login/'), name='panier_afficher', ),

    url(r'^panier/ajouter/(?P<produit_id>[0-9]+)/(?P<quantite>[0-9]{1,3}([.]{0,1}[0-9]{0,3}))/$',
        login_required(views.ajouterAuPanier, login_url='/auth/login/'), name='produit_ajouterAuPanier', ),

    url(r'^panier/supprimerItem/(?P<item_id>[0-9]+)',
        login_required(views.enlever_du_panier, login_url='/auth/login/'), name='supprimerDuPanier', ),

    url(r'^requetes/afficher/$',
        login_required(views.afficher_requetes, login_url='/auth/login/'), name='afficher_requetes', ),

    url(r'^conversations/(?P<destinataire>[-\w]+)$', views.lireConversation, name='lireConversation'),
    url(r'^conversations/(?P<destinataire1>[-\w]+)/(?P<destinataire2>[-\w]+)$', views.lireConversation_2noms, name='lireConversation_2noms'),
    url(r'^conversations/$', login_required(views.ListeConversations.as_view(), login_url='/auth/login/'), name='conversations'),
]

from django.conf.urls.static import static
from django.conf import settings
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls)),] + urlpatterns
    #urlpatterns += url('',(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
# if settings.DEBUG:
#     # static files (img, css, javascript, etc.)
#     urlpatterns += patterns('',
#         (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT}))