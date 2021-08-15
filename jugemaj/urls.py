"""Django URLs for the jugemaj app."""
from django.urls import path

from .views import CandidateCreateView, ElectionCreateView, ElectionDetailView, ElectionListView, vote

app_name = 'jugemaj'
urlpatterns = [
    path('', ElectionListView.as_view(), name='elections'),
    path('election', ElectionCreateView.as_view(), name='create_election'),
    path('election/<slug:slug>', ElectionDetailView.as_view(), name='election'),
    path('election/<slug:slug>/candidate', CandidateCreateView.as_view(), name='create_candidate'),
    path('election/<slug:slug>/vote', vote, name='vote'),
    path('candidate/<slug:slug>', vote, name='candidate'),
]
