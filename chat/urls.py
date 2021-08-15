from django.urls import path

from chat import views


urlpatterns = [
    path('', views.index),

    path('<str:room_name>/', views.room, name='room'),
]
