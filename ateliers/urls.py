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

app_name = 'ateliers'

urlpatterns = [
    url(r'^accueil-ateliers/$', views.accueil, name="acceuil"),
    url(r'^liste/$', views.ListeAteliers.as_view(), name="index_ateliers"),
    url(r'^atelier/(?P<slug>[-\w]+)$', views.lireAtelier_slug, name='lireAtelier'),
    url(r'^atelier/id/(?P<id>[-\w]+)$', views.lireAtelier_id, name='lireAtelier_id'),
    url(r'^atelier/inscription/(?P<slug>[-\w]+)$', views.inscriptionAtelier, name='inscriptionAtelier'),
    url(r'^atelier/annulerInscription/(?P<slug>[-\w]+)$', views.annulerInscription, name='annulerInscription'),
    url(r'^atelier/contacterParticipantsAtelier/(?P<slug>[-\w]+)$', views.contacterParticipantsAtelier, name='contacterParticipantsAtelier'),

    url(r'^modifierAtelier/(?P<slug>[-\w]+)$', login_required(views.ModifierAtelier.as_view(), login_url='/auth/login/'), name='modifierAtelier'),
    url(r'^modifierCommentaire/(?P<id>[0-9]+)$', login_required(views.ModifierCommentaire.as_view(), login_url='/auth/login/'), name='modifierCommentaireAtelier'),
    url(r'^supprimerAtelier/(?P<slug>[-\w]+)$', login_required(views.SupprimerAtelier.as_view(), login_url='/auth/login/'), name='supprimerAtelier'),
    url(r'^ajouterAtelier/(?P<article_slug>[-\w]+)$', login_required(views.ajouterAtelier), name='ajouterAtelier_article'),
    url(r'^ajouterAtelier/$', login_required(views.ajouterAtelier), name='ajouterAtelier'),

    url(r'^suivre_ateliers/$', views.suivre_ateliers, name='suivre_ateliers'),
]
