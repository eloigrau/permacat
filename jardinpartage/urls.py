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
    1. Add an import:  from jardinpartage__ import urls as jardinpartage_urls
    2. Add a URL to urlpatterns:  url(r'^jardinpartage__/', include(jardinpartage_urls))
"""
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'jardinpartage'

urlpatterns = [
    url(r'^accueil/$', views.accueil, name="forum"),
    url(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    path(r'articles/<str:jardin>', login_required(views.ListeArticles_jardin.as_view(), login_url='/auth/login/'), name="index_jardin"),
    # url(r'^newPost/', views.ajouterArticle, name='ajouterArticle'),
    # url(r'^article/(?P<slug>.+)$', views.lire, name='lire'),

    url(r'^article/(?P<slug>[-\w]+)$', views.lireArticle, name='lireArticle'),
    url(r'^accepter_participation$', views.accepter_participation, name='accepter_participation'),
    url(r'^modifierArticle/(?P<slug>[-\w]+)$', login_required(views.ModifierArticle.as_view(), login_url='/auth/login/'), name='modifierArticle'),
    url(r'^suiveursArticle/(?P<slug>[-\w]+)$', views.articles_suivis, name='suiveursArticle'),
    url(r'^suiveursArticles/$', views.articles_suiveurs, name='suiveursArticles'),
    url(r'^supprimerArticle/(?P<slug>[-\w]+)$', login_required(views.SupprimerArticle.as_view(), login_url='/auth/login/'), name='supprimerArticle'),
    url(r'^ajouterArticle/$', login_required(views.ajouterArticle), name='ajouterNouvelArticle'),

    url(r'^suivre_article/(?P<slug>[-\w]+)/$', views.suivre_article, name='suivre_article'),
    url(r'^suivre_articles/$', views.suivre_articles, name='suivre_articles'),

    url(r'^modifierCommentaireArticle/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireArticle.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireArticle'),

    url(r'ajouterEvenement/$', views.ajouterEvenement, name='ajouterEvenement'),
    path(r'ajouterEvenementArticle/<str:slug_article>', views.ajouterEvenementArticle, name='ajouterEvenementArticle'),
    path(r'ajouterSalonArticle/<str:slug_article>', views.ajouterEvenementArticle, name='ajouterEvenementArticle'),

]
