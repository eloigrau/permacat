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

app_name = 'blog'

urlpatterns = [
    url(r'^accueil/$', views.accueil, name="forum"),
    url(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    # url(r'^newPost/', views.ajouterNouveauPost, name='ajouterNouveauPost'),
    # url(r'^article/(?P<slug>.+)$', views.lire, name='lire'),

    url(r'^article/(?P<slug>[-\w]+)$', views.lireArticle, name='lireArticle'),
    url(r'^modifierArticle/(?P<slug>[-\w]+)$', login_required(views.ModifierArticle.as_view(), login_url='/auth/login/'), name='modifierArticle'),
    url(r'^suiveursArticle/(?P<slug>[-\w]+)$', views.articles_suivis, name='suiveursArticle'),
    url(r'^suiveursProjet/(?P<slug>[-\w]+)$', views.projets_suivis, name='suiveursProjet'),
    url(r'^supprimerArticle/(?P<slug>[-\w]+)$', login_required(views.SupprimerArticle.as_view(), login_url='/auth/login/'), name='supprimerArticle'),
    url(r'^ajouterArticle/$', views.ajouterNouveauPost, name='ajouterNouvelArticle'),

    url(r'^projets/$', login_required(views.ListeProjets.as_view(), login_url='/auth/login/'), name="index_projets"),
    url(r'^projets/(?P<slug>[-\w]+)$', views.lireProjet, name='lireProjet'),
    url(r'^modifierProjet/(?P<slug>[-\w]+)$',
        login_required(views.ModifierProjet.as_view(), login_url='/auth/login/'), name='modifierProjet'),
    url(r'^supprimerProjet/(?P<slug>[-\w]+)$',
        login_required(views.SupprimerProjet.as_view(), login_url='/auth/login/'), name='supprimerProjet'),
    url(r'^ajouterProjet/$', views.ajouterNouveauProjet, name='ajouterNouveauProjet'),
    url(r'^telecharger_fichier/$', views.telecharger_fichier, name='telechargerFichier'),

    url(r'^suivre_article/(?P<slug>[-\w]+)/$', views.suivre_article, name='suivre_article'),
    url(r'^suivre_projet/(?P<slug>[-\w]+)/$', views.suivre_projet, name='suivre_projet'),
    url(r'^suivre_articles/$', views.suivre_articles, name='suivre_articles'),
    url(r'^suivre_projets/$', views.suivre_projets, name='suivre_projets'),


]
