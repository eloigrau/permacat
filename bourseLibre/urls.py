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
from django.views.generic import TemplateView
from bourseLibre.views import handler400 as h400, handler403  as h403, handler404  as h404, handler500  as h500
#from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

# On import les vues de Django, avec un nom spécifique
from django.contrib.auth.decorators import login_required

# admin.autodiscover()
from django.contrib import admin

#from wiki import urls

admin.sites.site_header ="Admin "
admin.sites.site_title ="Admin Permacat"


urlpatterns = [
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^captcha/', include('bourseLibre.captcha_local.urls')),
    path(r'agenda/', include('cal.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^$', views.bienvenue, name='bienvenue'),
    url(r'^bienvenue/$', views.bienvenue, name='bienvenue'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^gallerie/$', views.gallerie, name='gallerie'),
    url(r'^permacat/admin/$', views.admin_asso, name='admin_asso'),
    url(r'^RTG/admin/$', views.admin_asso_rtg, name='admin_asso_rtg'),
    url(r'^permacat/fichiers/$', views.telechargements_asso, name='telechargements_asso'),
    url(r'^permacat/adhesion_asso/$', views.adhesion_asso, name='adhesion_asso'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^notifications/news/$', views.notifications_news, name='notifications_news'),
    url(r'^notificationsParDate/$', views.notificationsParDate, name='notificationsParDate'),
    url(r'^notificationsLues/$', views.notificationsLues, name='notificationsLues'),
    url(r'^dernieresInfos/$', views.dernieresInfos, name='dernieresInfos'),
    url(r'^prochaines_rencontres/$', views.prochaines_rencontres, name='prochaines_rencontres'),
    url(r'^permacat/presentation/$', views.presentation_asso, name='presentation_asso'),
    url(r'^site/presentation/$', views.presentation_site, name='presentation_site'),
    url(r'^permacat/statuts/$', views.statuts, name='statuts'),
    url(r'^ramenetagraine/statuts/$', views.statuts_rtg, name='statuts_rtg'),

    url(r'^gestion/', admin.site.urls, name='admin',),
    url(r'^merci/$', views.merci, name='merci'),
    url(r'^forum/', include('blog.urls', namespace='bourseLibre.blog')),
    url(r'^jardins/', include('jardinpartage.urls', namespace='bourseLibre.jardinpartage')),
    url(r'^vote/', include('vote.urls', namespace='bourseLibre.vote')),
    url(r'^kit/', include('fiches.urls', namespace='bourseLibre.fiches')),
    url(r'^ateliers/', include('ateliers.urls', namespace='bourseLibre.ateliers')),
    # url(r'^search/', include('haystack.urls'), name='chercher_site'),
    #url(r'^search/', include('haystack.urls'), name='haystack_search'),
    url(r'^chercher/produit/$', login_required(views.chercher), name='chercher'),
    url(r'^accounts/profil/(?P<user_id>[0-9]+)/$', login_required(views.profil), name='profil',),
    url(r'^accounts/profil/(?P<user_username>[\w.@+-]+)/$', login_required(views.profil_nom), name='profil_nom',),
    url(r'^accounts/profile/$',  login_required(views.profil_courant), name='profil_courant',),
    url(r'^accounts/profil_inconnu/$', views.profil_inconnu, name='profil_inconnu',),
    url(r'^accounts/profil_modifier/$', login_required(views.profil_modifier.as_view()), name='profil_modifier',),
    url(r'^accounts/profil_supprimer/$', login_required(views.profil_supprimer.as_view()), name='profil_supprimer',),
    url(r'^accounts/profil_modifier_adresse/$', login_required(views.profil_modifier_adresse.as_view()), name='profil_modifier_adresse',),
    url(r'^accounts/profil_contact/(?P<user_id>[0-9]+)/$', login_required(views.profil_contact), name='profil_contact',),
    url(r'^accounts/mesSuivis$', login_required(views.mesSuivis), name='mesSuivis',),
    url(r'^register/$', views.register, name='senregistrer',),
    #url(r'^password/reset/$', views.reset_password, name='reset_password'),
    url(r'^password/change/$', views.change_password, name='change_password'),
    path('auth/', include('django.contrib.auth.urls')),

    url(r'^contact_admins/$', views.contact_admins, name='contact_admins',),
    url(r'^charte/$', views.charte, name='charte',),
    url(r'^cgu/$', views.cgu, name='cgu',),
    url(r'^liens/$', views.liens, name='liens',),
    url(r'^fairedon/$', views.fairedon, name='fairedon',),
    #url(r'^agenda/$', views.agenda, name='agenda',),
    url(r'^cooperateurs/annuaire/$', login_required(views.annuaire), name='annuaire',),
    url(r'^cooperateurs/listeContacts/$', login_required(views.listeContacts), name='listeContacts',),
    url(r'^cooperateurs/listeContacts_rtg/$', login_required(views.listeContacts_rtg), name='listeContacts_rtg',),
    url(r'^cooperateurs/listeFollowers/$', login_required(views.listeFollowers), name='listeFollowers',),
    url(r'^cooperateurs/annuaire_permacat/$', login_required(views.annuaire_permacat), name='annuaire_permacat',),
    url(r'^cooperateurs/annuaire_rtg/$', login_required(views.annuaire_rtg), name='annuaire_rtg',),
    url(r'^cooperateurs/carte/$', login_required(views.carte), name='carte',),
    url(r'^cooperateurs/carte_permacat/$', login_required(views.carte_permacat), name='carte_permacat',),
    url(r'^cooperateurs/carte_rtg/$', login_required(views.carte_rtg), name='carte_rtg',),

    url(r'^cooperateurs/contacter_newsletter/$', login_required(views.contacter_newsletter), name='contacter_newsletter',),
    url(r'^cooperateurs/contacter_adherents/$', login_required(views.contacter_adherents), name='contacter_adherents',),
    url(r'^cooperateurs/contacter_adherents_rtg/$', login_required(views.contacter_adherents_rtg), name='contacter_adherents_rtg',),

    url(r'^marche/proposer/(?P<type_produit>[-A-Za-z]+)/$', login_required(views.produit_proposer), name='produit_proposer', ),
    url(r'^marche/proposer/', login_required(views.proposerProduit_entree), name='produit_proposer_entree',),

    # url(r'^list$', views.product_list),
    #     url(r'^list2/$', FilterView.as_view(model=Produit, filterset_class=ProductFilter,)),
    url(r'^marche/$', login_required(views.ListeProduit.as_view()),  name="marche"),
    url(r'^marche/lister/$', login_required(views.ListeProduit.as_view()),  name="marche"),
    url(r'^marche/supprimerProduits_expires_confirmation/$', views.supprimerProduits_expires_confirmation,  name="supprimerProduits_expires_confirmation"),
    url(r'^marche/supprimerProduits_expires/$', views.supprimerProduits_expires,  name="supprimerProduits_expires"),
    url(r'^marche/lister_offres/', login_required(views.ListeProduit_offres.as_view()),
        name="marche_offres"),
    url(r'^marche/lister_recherches/', login_required(views.ListeProduit_recherches.as_view()),
        name="marche_recherches"),

    url(r'^marche/detail/(?P<produit_id>[0-9]+)/$', login_required(views.detailProduit), name='produit_detail',),

    url(r'^marche/modifier/(?P<pk>[0-9]+)/$',
        login_required(views.ProduitModifier.as_view()), name='produit_modifier', ),
    url(r'^marche/contacterProducteur/(?P<producteur_id>[0-9]+)/$',
        login_required(views.produitContacterProducteur), name='produit_contacterProducteur', ),
    url(r'^marche/supprimer/(?P<pk>[0-9]+)/$',
        login_required(views.ProduitSupprimer.as_view()), name='produit_supprimer', ),

    url(r'^panier/afficher/$', login_required(views.afficher_panier), name='panier_afficher', ),

    url(r'^panier/ajouter/(?P<produit_id>[0-9]+)/(?P<quantite>[0-9]{1,3}([.]{0,1}[0-9]{0,3}))/$',
        login_required(views.ajouterAuPanier), name='produit_ajouterAuPanier', ),

    url(r'^panier/supprimerItem/(?P<item_id>[0-9]+)',
        login_required(views.enlever_du_panier), name='supprimerDuPanier', ),

    url(r'^requetes/afficher/$',
        login_required(views.afficher_requetes), name='afficher_requetes', ),

    url(r'^conversations/(?P<destinataire>[\w.@+-]+)$', login_required(views.lireConversation), name='agora_conversation'),
    url(r'^conversations/(?P<destinataire1>[\w.@+-]+)/(?P<destinataire2>[\w.@+-]+)$', login_required(views.lireConversation_2noms), name='lireConversation_2noms'),
    url(r'^conversations/$', login_required(views.ListeConversations.as_view()), name='conversations'),
    url(r'^conversations/chercher/$', login_required(views.chercherConversation), name='chercher_conversation'),
    url(r'^suivre_conversation/$', views.suivre_conversations, name='suivre_conversations'),
    url(r'^suivre_produits/$', views.suivre_produits, name='suivre_produits'),

    url(r'^agora/$', login_required(views.agora), name='agora_general'),
    url(r'^agora_permacat/$', login_required(views.agora_permacat), name='agora_permacat'),
    url(r'^agora_rtg/$', login_required(views.agora_rtg), name='agora_rtg'),

    url(r'^activity/', include('actstream.urls')),

#    path(r'wiki_ecovillage_notifications/', include('django_nyt.urls')),
#    path(r'wiki_ecovillage/', include('wiki.urls')),


    url(r'^inscription_newsletter/$', views.inscription_newsletter, name='inscription_newsletter', ),

    url(r'^modifierMessage/(?P<id>[0-9]+)(?P<type>[-\w.]+)$', views.modifier_message, name='modifierMessage'),
]
urlpatterns += [
    url(r'^robots\.txt$', TemplateView.as_view(template_name="bourseLibre/robots.txt", content_type='text/plain')),
]

from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = h404
handler500 = h500
handler400 = h400
handler403 = h403

if settings.LOCALL:
    import debug_toolbar
    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls)),] + urlpatterns
    #urlpatterns += url('',(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))

