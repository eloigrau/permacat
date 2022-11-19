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

from bourseLibre import views_inscriptions
from . import views, forms
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView

app_name = 'blog'

urlpatterns = [
    url(r'^accueil/$', views.accueil, name="acceuil"),
    url(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    path(r'articles/<str:asso>', login_required(views.ListeArticles_asso.as_view(), login_url='/auth/login/'), name="index_asso"),
    # url(r'^newPost/', views.ajouterArticle, name='ajouterArticle'),
    # url(r'^article/(?P<slug>.+)$', views.lire, name='lire'),

    path(r'article/<str:slug>', views.lireArticle, name='lireArticle'),
    path(r'article/<int:id>', views.lireArticle_id, name='lireArticle_id'),
    url(r'^modifierArticle/(?P<slug>[-\w]+)$', login_required(views.ModifierArticle.as_view(), login_url='/auth/login/'), name='modifierArticle'),
    url(r'^Article/AjouterAlbum/(?P<slug>[-\w]+)$', login_required(views.ArticleAddAlbum.as_view(), login_url='/auth/login/'), name='ajouterAlbumArticle'),
    url(r'^Article/SupprimerAlbum/(?P<slug>[-\w]+)$', views.articleSupprimerAlbum, name='supprimerAlbumArticle'),
    url(r'^suiveursArticle/(?P<slug>[-\w]+)$', views.articles_suivis, name='suiveursArticle'),
    url(r'^suiveursArticles/$', views.articles_suiveurs, name='suiveursArticles'),
    url(r'^suiveursProjet/(?P<slug>[-\w]+)$', views.projets_suivis, name='suiveursProjet'),
    url(r'^supprimerArticle/(?P<slug>[-\w]+)$', login_required(views.SupprimerArticle.as_view(), login_url='/auth/login/'), name='supprimerArticle'),
    url(r'^ajouterArticle/$', login_required(views.ajouterArticle), name='ajouterNouvelArticle'),
    path(r'archiverArticleAdmin/<str:slug>', login_required(views.archiverArticleAdmin), name='archiverArticleAdmin'),
    #path('post/', forms.ArticleFormPreview(forms.ArticleForm)),

    url(r'^projets/$', login_required(views.ListeProjets.as_view(), login_url='/auth/login/'), name="index_projets"),
    url(r'^projets/(?P<slug>[-\w]+)$', views.lireProjet, name='lireProjet'),
    url(r'^modifierProjet/(?P<slug>[-\w]+)$',
        login_required(views.ModifierProjet.as_view(), login_url='/auth/login/'), name='modifierProjet'),
    url(r'^supprimerProjet/(?P<slug>[-\w]+)$',
        login_required(views.SupprimerProjet.as_view(), login_url='/auth/login/'), name='supprimerProjet'),
    url(r'^ajouterProjet/$', views.ajouterNouveauProjet, name='ajouterNouveauProjet'),
    path(r'projets/ajouterFicheProjet/<str:slug>', views.ajouterFicheProjet, name='ajouterFicheProjet'),
    path(r'projets/modifier/<str:slug>',
        login_required(views.ModifierFicheProjet.as_view(), login_url='/auth/login/'), name='modifierFicheProjet'),
    path(r'projets/supprimer/<str:slug>',
        login_required(views.SupprimerFicheProjet.as_view(), login_url='/auth/login/'), name='supprimerFicheProjet'),
    url(r'^telecharger_fichier/$', views.telecharger_fichier, name='telechargerFichier'),

    url(r'^suivre_article/(?P<slug>[-\w]+)/$', views.suivre_article, name='suivre_article'),
    url(r'^suivre_projet/(?P<slug>[-\w]+)/$', views.suivre_projet, name='suivre_projet'),
    path(r'suivre_agora/<str:asso_abreviation>', views.suivre_articles, name='suivre_articles'),
    url(r'^suivre_projets/$', views.suivre_projets, name='suivre_projets'),
    url(r'^filtrer_articles/$', views.filtrer_articles, name='filtrer_articles'),

    url(r'^modifierCommentaireArticle/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireArticle.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireArticle'),
    url(r'^modifierCommentaireProjet/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireProjet.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireProjet'),

    url(r'ajouterEvenement/$', views.ajouterEvenement, name='ajouterEvenement'),
    url(r'transfereArticlesJardin/$', views.changerArticles_jardin, name='transfereArticlesJardin'),
    path(r'ajouterEvenementArticle/<str:slug_article>', views.ajouterEvenementArticle, name='ajouterEvenementArticle'),
    path(r'ajouterSalonArticle/<str:slug_article>', views.ajouterSalonArticle, name='ajouterSalonArticle'),
    url(r'^supprimerEvenementArticle/(?P<slug_article>[-\w]+)-(?P<id_evenementArticle>[0-9]+)$', login_required(views.SupprimerEvenementArticle.as_view(), login_url='/auth/login/'), name='supprimerEvenementArticle'),
    url(r'ajouterAdresseArticle/(?P<id_article>[0-9]+)$', views.ajouterAdresseArticle, name='ajouterAdresseArticle'),
    url(r'^supprimerAdresseArticle/(?P<slug_article>[-\w]+)/(?P<id_adresse>[0-9]+)$', login_required(views.SupprimerAdresseArticle.as_view(), login_url='/auth/login/'), name='supprimerAdresseArticle'),
    url(r'voirCarteLieux/(?P<id_article>[0-9]+)$', views.voirCarteLieux, name='voirCarteLieux'),

    path('ajax/load-categories/', views.ajax_categories, name='ajax_categories'),
    url(r'voirTousLieux/$', views.voirLieux, name='voirTousLieux'),


]
