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
    1. Add an import:  from vote__ import urls as vote_urls
    2. Add a URL to urlpatterns:  url(r'^vote__/', include(vote_urls))
"""
from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'vote'

urlpatterns = [
    url(r'^accueil/$', views.accueil, name="accueil"),
    url(r'^votations/$', login_required(views.ListeVotations.as_view(), login_url='/auth/login/'), name="index"),
    url(r'^votation/(?P<slug>[-\w]+)$', views.lireVotation, name='lireVotation'),
    url(r'^modifierVotation/(?P<slug>[-\w]+)$', login_required(views.ModifierVotation.as_view(), login_url='/auth/login/'), name='modifierVotation'),
    url(r'^supprimerVotation/(?P<slug>[-\w]+)$',
        login_required(views.SupprimerVotation.as_view(), login_url='/auth/login/'), name='supprimerVotation'),

    url(r'^ajouterVotation/$', login_required(views.ajouterVotation), name='ajouterNouvelVotation'),
    url(r'^voter/(?P<slug>[-\w]+)$', login_required(views.voter), name='voter'),
    url(r'^modifierVote/(?P<slug>[-\w]+)$', login_required(views.ModifierVote.as_view(), login_url='/auth/login/'), name='modifierVote'),
    url(r'^votation/resultat/(?P<slug>[-\w]+)$', views.resultatsVotation, name='resultatsVotation'),
    url(r'^modifierCommentaireVotation/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireVotation.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireVotation'),
]
