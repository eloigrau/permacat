from django.conf.urls import url
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from . import views


"""NOTE: the url names are changing. In the long term, I want to remove the 'pl-'
prefix on all urls, and instead rely on an application namespace 'photologue'.

At the same time, I want to change some URL patterns, e.g. for pagination. Changing the urls
twice within a few releases, could be confusing, so instead I am updating URLs bit by bit.

The new style will coexist with the existing 'pl-' prefix for a couple of releases.

"""


app_name = 'photologue'
urlpatterns = [
    url(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', views.AlbumDateDetailView.as_view(month_format='%m'), name='album-detail'),
    url(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$', views.AlbumDayArchiveView.as_view(month_format='%m'), name='album-archive-day'),
    url(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/$', views.AlbumMonthArchiveView.as_view(month_format='%m'), name='album-archive-month'),
    url(r'^album/(?P<year>\d{4})/$', views.AlbumYearArchiveView.as_view(), name='pl-album-archive-year'),
    url(r'^album/$', views.AlbumArchiveIndexView.as_view(), name='pl-album-archive'),
    url(r'^$', RedirectView.as_view( url=reverse_lazy('photologue:pl-album-archive'), permanent=True), name='pl-photologue-root'),
    url(r'^album/(?P<slug>[\-\d\w]+)/$', views.AlbumDetailView.as_view(), name='pl-album'),
    url(r'^albumlist/$', views.AlbumListView.as_view(), name='album-list'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', views.PhotoDateDetailView.as_view(month_format='%m'),
        name='photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$', views.PhotoDayArchiveView.as_view(month_format='%m'), name='photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/$', views.PhotoMonthArchiveView.as_view(month_format='%m'), name='photo-archive-month'),
    url(r'^photo/(?P<year>\d{4})/$', views.PhotoYearArchiveView.as_view(), name='pl-photo-archive-year'),
    url(r'^photo/$', views.PhotoArchiveIndexView.as_view(), name='pl-photo-archive'),

    url(r'^photo/(?P<slug>[\-\d\w]+)/$', views.PhotoDetailView.as_view(), name='pl-photo'),
    url(r'^photolist/$', views.PhotoListView.as_view(), name='photo-list'),
    url(r'^ajouterPhoto/(?P<albumSlug>[\-\d\w]+)$', login_required(views.ajouterPhoto), name='ajouterPhoto'),
    url(r'^ajouterAlbum/$', login_required(views.ajouterAlbum), name='ajouterAlbum'),

    url(r'^modifierAlbum/(?P<slug>[\-\d\w]+)$', login_required(views.ModifierAlbum.as_view(), login_url='/auth/login/'), name='modifierAlbum'),
    url(r'^supprimerAlbum/(?P<slug>[\-\d\w]+)$', login_required(views.SupprimerAlbum.as_view(), login_url='/auth/login/'), name='supprimerAlbum'),
    url(r'^modifierPhoto/(?P<slug>[\-\d\w]+)$', login_required(views.ModifierPhoto.as_view(), login_url='/auth/login/'), name='modifierPhoto'),
    url(r'^supprimerPhoto/(?P<slug>[\-\d\w]+)$', login_required(views.SupprimerPhoto.as_view(), login_url='/auth/login/'), name='supprimerPhoto'),

]
