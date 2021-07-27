# cal/urls.py

from django.conf.urls import url
from . import views

app_name = 'carto'
urlpatterns = [
    url(r'', views.carte, name='carte'),
]
