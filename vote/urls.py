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
from django.urls import path
from . import views#, views_wizard
from django.contrib.auth.decorators import login_required


app_name = 'vote'

urlpatterns = [
    url(r'^$', views.accueil, name="accueil"),
    url(r'^suffrages/$', login_required(views.ListeSuffrages.as_view(), login_url='/auth/login/'), name="index"),
    url(r'^suffrage/(?P<slug>[-\w]+)$', views.lireSuffrage, name='lireSuffrage'),
    url(r'^modifierSuffrage/(?P<slug>[-\w]+)$', login_required(views.ModifierSuffrage.as_view(), login_url='/auth/login/'), name='modifierSuffrage'),
    url(r'^supprimerSuffrage/(?P<slug>[-\w]+)$',
        login_required(views.SupprimerSuffrage.as_view(), login_url='/auth/login/'), name='supprimerSuffrage'),

    path(r'ajouterSuffrage/<str:article_slug>', login_required(views.ajouterSuffrage), name='ajouterSuffrage'),
    url(r'^voter/(?P<slug>[-\w]+)$', login_required(views.voter), name='voter'),
    url(r'^modifierVote/(?P<slug>[-\w]+)$', login_required(views.ModifierVote.as_view(), login_url='/auth/login/'), name='modifierVote'),
    url(r'^suffrage/resultat/(?P<slug>[-\w]+)$', views.resultatsSuffrage, name='resultatsSuffrage'),
    url(r'^modifierCommentaireSuffrage/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireSuffrage.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireSuffrage'),
    url(r'^suivre_suffrages/$', views.suivre_suffrages, name='suivre_suffrages'),
    url(r'^suffrage/(?P<slug>[-\w]+)/ajouterQuestion$', views.ajouterQuestion, name='ajouterQuestion'),
    url(r'^suffrage/(?P<slug>[-\w]+)/ajouterQuestionB$', views.ajouterQuestionB, name='ajouterQuestionB'),
    url(r'^suffrage/(?P<slug>[-\w]+)/ajouterQuestionM$', views.ajouterQuestionM, name='ajouterQuestionM'),

    path(r'supprimerQuestionB/<str:slug>/<int:id_question>', views.supprimerQuestionB, name='supprimerQuestionB'),
    path(r'supprimerQuestionM/<str:slug>/<int:id_question>', views.supprimerQuestionM, name='supprimerQuestionM'),
    path(r'supprimerPropositionM/<str:slug><int:id_question>/<int:id_proposition>', views.supprimerPropositionM, name='supprimerPropositionM'),
    #url(r'ajouter_suffrage/$', views_wizard.SuffrageWizard.as_view()),


]
