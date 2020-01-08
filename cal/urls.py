# cal/urls.py

from django.conf.urls import url
from . import views

app_name = 'cal'
urlpatterns = [
    url(r'', views.agenda, name='agenda'),
]
