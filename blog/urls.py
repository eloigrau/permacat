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
    # url(r'^blog/index$', views.index, name='index'),
    #     url(r'^$', views.accueil, name='accueil'),
    #     url(r'^$', ListView.as_view(model=Article,), name='accueil2', template_name="accueil.html"),
    url(r'^acceuil/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="accueil"),
    # url(r'^newPost/', views.ajouterNouveauPost, name='ajouterNouveauPost'),
    # url(r'^article/(?P<slug>.+)$', views.lire, name='lire'),

    url(r'^articles/(?P<slug>[-\w]+)$', views.lireArticle, name='lireArticle'),
    url(r'^modifierArticle/(?P<slug>[-\w]+)$', login_required(views.ModifierArticle.as_view(), login_url='/auth/login/'), name='modifierArticle'),
    url(r'^ajouterarticle/$', views.ajouterNouveauPost, name='ajouterNouvelArticle'),
]