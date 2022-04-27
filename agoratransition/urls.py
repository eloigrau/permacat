# cal/urls.py

from django.conf.urls import url
from . import views
from django.urls import path
from django.contrib.auth.decorators import login_required

app_name = 'agora'

urlpatterns = [
    url(r'^$', views.accueil, name="acceuil"),
    url(r'^listeInscription/$', views.listeInscription, name="listeInscription"),
    #url(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    #path(r'articles/<str:asso>', login_required(views.ListeArticles_asso.as_view(), login_url='/auth/login/'), name="index_asso"),
    ]
