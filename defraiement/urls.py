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
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'defraiement'

urlpatterns = [
    #(r'^accueil/$', login_required(views.ListeReunions.as_view(), login_url='/auth/login/'), name="reunions"),
    url(r'^reunions/$', login_required(views.ListeReunions.as_view(), login_url='/auth/login/'), name="reunions"),
    path(r'reunions/<str:asso_slug>', login_required(views.ListeReunions_asso.as_view(), login_url='/auth/login/'), name="reunions_asso"),
    path(r'participants/<str:asso_slug>', login_required(views.ListeParticipants.as_view(), login_url='/auth/login/'), name="participants"),
    path(r'reunion/<str:slug>', views.lireReunion, name='lireReunion'),
    path(r'reunion/<int:id>', views.lireReunion_id, name='lireReunion_id'),
     url(r'^modifierAdresseReunion/(?P<slug>[-\w]+)$', views.modifierAdresseReunion, name='modifierAdresseReunion'),
     path(r'ajouterAdresseReunion/<str:slug>', views.ajouterAdresseReunion, name='ajouterAdresseReunion'),
     path(r'ajouterAdresseReunionChezParticipant/<str:slug>', views.ajouterAdresseReunionChezParticipant, name='ajouterAdresseReunionChezParticipant'),
     path(r'recalculerDistanceReunion/<str:slug_reunion>', views.recalculerDistanceReunion, name='recalculerDistanceReunion'),
    url(r'^modifierReunion/(?P<slug>[-\w]+)$',
        login_required(views.ModifierReunion.as_view(), login_url='/auth/login/'), name='modifierReunion'),
    url(r'^supprimerReunion/(?P<slug>[-\w]+)$', login_required(views.SupprimerReunion.as_view(), login_url='/auth/login/'), name='supprimerReunion'),
    path(r'ajouterReunion/<str:asso_slug>', login_required(views.ajouterReunion), name='ajouterReunion'),

    path(r'participant/<int:id>', views.lireParticipant, name='lireParticipant'),
    path(r'ajouterParticipant/<str:asso_slug>', views.ajouterParticipant, name='ajouterParticipant'),
    path(r'modifierParticipant/<int:id>',
        login_required(views.ModifierParticipant.as_view(), login_url='/auth/login/'), name='modifierParticipant'),
    path(r'modifierParticipantReunion/<int:id>', views.modifierParticipantReunion, name='modifierParticipantReunion'),

    path(r'supprimerParticipant/<int:id>',
        login_required(views.SupprimerParticipant.as_view(), login_url='/auth/login/'), name='supprimerParticipant'),

    path(r'ajouterParticipantReunion/<str:slug_reunion>', views.ajouterParticipantReunion, name='ajouterParticipantReunion'),
    path(r'ajouterParticipantsReunion/<str:slug_reunion>', views.ajouterParticipantsReunion, name='ajouterParticipantsReunion'),
    path(r'supprimerParticipantReunion/<str:slug_reunion>/<int:id_participantReunion>', login_required(views.SupprimerParticipantReunion.as_view(), login_url='/auth/login/'), name='supprimerParticipantReunion'),

    path(r'recapitulatif/<str:asso_slug>/', views.recapitulatif, name='recapitulatif'),
    path(r'export_recapitulatif/<str:asso>/<str:type_reunion>/', views.export_recapitulatif, name='export_recapitulatif'),

    url(r'voirTousLieux/$', views.voirLieux, name='voirTousLieux'),
]
