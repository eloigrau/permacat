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
    url(r'^reunions/$', login_required(views.ListeReunions.as_view(), login_url='/auth/login/'), name="reunions"),
    path(r'reunion/<str:slug>', views.lireReunion, name='lireReunion'),
    path(r'reunion/<int:id>', views.lireReunion_id, name='lireReunion_id'),
    url(r'^modifierReunion/(?P<slug>[-\w]+)$', login_required(views.ModifierReunion.as_view(), login_url='/auth/login/'), name='modifierReunion'),
    url(r'^modifierAdresseReunion/(?P<slug>[-\w]+)$', views.modifierAdresseReunion, name='modifierAdresseReunion'),
    url(r'^ajouterAdresseReunion/(?P<slug>[-\w]+)$', views.ajouterAdresseReunion, name='ajouterAdresseReunion'),
    url(r'^supprimerReunion/(?P<slug>[-\w]+)$', login_required(views.SupprimerReunion.as_view(), login_url='/auth/login/'), name='supprimerReunion'),
    url(r'^ajouterReunion/$', login_required(views.ajouterReunion), name='ajouterReunion'),


    path(r'ajouterParticipantReunion/<str:slug_reunion>', views.ajouterParticipantReunion, name='ajouterParticipantReunion'),
    path(r'supprimerParticipantReunion/<str:slug_reunion>/<int:id_participantReunion>', login_required(views.SupprimerParticipantReunion.as_view(), login_url='/auth/login/'), name='supprimerParticipantReunion'),

    url(r'recapitulatif/$', views.recapitulatif, name='recapitulatif'),
    url(r'export_recapitulatif/$', views.export_recapitulatif, name='export_recapitulatif'),
    url(r'voirTousLieux/$', views.voirLieux, name='voirTousLieux'),
]
