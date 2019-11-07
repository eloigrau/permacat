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
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'fiches'

urlpatterns = [
    url(r'^accueil/$', views.accueil, name="acceuil"),
    url(r'^fiches/$', login_required(views.ListeFiches.as_view(), login_url='/auth/login/'), name="index"),
    url(r'^ateliers/$', login_required(views.ListeAteliers.as_view(), login_url='/auth/login/'), name="index_ateliers"),
    url(r'^fiche/(?P<slug>[-\w]+)$', views.lireFiche, name='lireFiche'),
    url(r'^modifierFiche/(?P<slug>[-\w]+)$', login_required(views.ModifierFiche.as_view(), login_url='/auth/login/'), name='modifierFiche'),
    url(r'^modifierAtelier/(?P<slug>[-\w]+)$', login_required(views.ModifierAtelier.as_view(), login_url='/auth/login/'), name='modifierAtelier'),
    url(r'^supprimerFiche/(?P<slug>[-\w]+)$', login_required(views.SupprimerFiche.as_view(), login_url='/auth/login/'), name='supprimerFiche'),
    url(r'^ajouterFiche/$', login_required(views.ajouterFiche), name='ajouterFiche'),
    url(r'^ajouterAtelier/(?P<fiche_slug>[-\w]+)$', login_required(views.ajouterAtelier), name='ajouterAtelier'),
]
