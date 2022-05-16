# cal/urls.py

from . import views
from django.urls import path
from django.conf.urls import include, url

app_name = 'agora'

urlpatterns = [
    url(r'^$', views.accueil, name="acceuil"),
    url(r'^listeInscription/$', views.listeInscription, name="listeInscription"),
    #url(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    #path(r'articles/<str:asso>', login_required(views.ListeArticles_asso.as_view(), login_url='/auth/login/'), name="index_asso"),
    ]

from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'inscriptions_at', views.InscriptionsViewSet)
urlpatterns += [
    path('api/', include(router.urls)),
    path('api_annonces/', include('rest_framework.urls', namespace='rest_framework')),
]