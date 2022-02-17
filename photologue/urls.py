from django.conf.urls import url
from django.urls import path
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from . import views


"""NOTE: the url names are changing. In the long term, I want to remove the ''
prefix on all urls, and instead rely on an application namespace 'photologue'.

At the same time, I want to change some URL patterns, e.g. for pagination. Changing the urls
twice within a few releases, could be confusing, so instead I am updating URLs bit by bit.

The new style will coexist with the existing '' prefix for a couple of releases.

"""


app_name = 'photologue'

urlpatterns = [
    url(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', login_required(views.AlbumDateDetailView.as_view(month_format='%m')), name='album-detail'),
    url(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$', login_required(views.AlbumDayArchiveView.as_view(month_format='%m')), name='album-archive-day'),
    url(r'^album/(?P<year>\d{4})/(?P<month>[0-9]{2})/$', login_required(views.AlbumMonthArchiveView.as_view(month_format='%m')), name='album-archive-month'),
    url(r'^album/(?P<year>\d{4})/$', login_required(views.AlbumYearArchiveView.as_view()), name='album-archive-year'),
    url(r'^album/$', login_required(views.AlbumArchiveIndexView.as_view()), name='album-archive'),
    url(r'^$', RedirectView.as_view( url=reverse_lazy('photologue:album-archive'), permanent=True), name='photologue-root'),
    url(r'^album/(?P<slug>[\-\d\w]+)/$', login_required(views.AlbumDetailView.as_view()), name='album'),
    url(r'^albumlist/$', login_required(views.AlbumListView.as_view()), name='album-list'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', login_required(views.PhotoDateDetailView.as_view(month_format='%m')),
        name='photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$', login_required(views.PhotoDayArchiveView.as_view(month_format='%m')), name='photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/$', login_required(views.PhotoMonthArchiveView.as_view(month_format='%m')), name='photo-archive-month'),
    url(r'^photo/(?P<year>\d{4})/$', login_required(views.PhotoYearArchiveView.as_view()), name='photo-archive-year'),
    url(r'^photo/$', login_required(views.PhotoArchiveIndexView.as_view()), name='photo-archive'),

    url(r'^photo/(?P<slug>[\-\d\w]+)/$', login_required(views.PhotoDetailView.as_view()), name='photo'),
    url(r'^photolist/$', login_required(views.PhotoListView.as_view()), name='photo-list'),
    url(r'^doclist/$', login_required(views.DocListView.as_view()), name='doc-list'),
    url(r'^filtrer_documents/$', views.filtrer_documents, name='filtrer_documents'),
    url(r'^ajouterPhoto/(?P<albumSlug>[\-\d\w]+)$', views.ajouterPhoto, name='ajouterPhoto'),
    url(r'^ajouterAlbum/$', views.ajouterAlbum, name='ajouterAlbum'),
    path(r'ajouterDocument/<str:article_slug>', views.ajouterDocument, name='ajouterDocument'),
    path(r'associerDocumentArticle/<str:doc_slug>', views.associerDocumentArticle, name='associerDocumentArticle'),

    url(r'^modifierAlbum/(?P<slug>[\-\d\w]+)$', login_required(views.ModifierAlbum.as_view(), login_url='/auth/login/'), name='modifierAlbum'),
    url(r'^supprimerAlbum/(?P<slug>[\-\d\w]+)$', login_required(views.SupprimerAlbum.as_view(), login_url='/auth/login/'), name='supprimerAlbum'),
    url(r'^modifierPhoto/(?P<slug>[\-\d\w]+)$', login_required(views.ModifierPhoto.as_view(), login_url='/auth/login/'), name='modifierPhoto'),
    url(r'^supprimerPhoto/(?P<slug>[\-\d\w]+)$', login_required(views.SupprimerPhoto.as_view(), login_url='/auth/login/'), name='supprimerPhoto'),

    url(r'^supprimerDocument/(?P<slug>[\-\d\w]+)$',
        login_required(views.SupprimerDocument.as_view(), login_url='/auth/login/'), name='supprimerDocument'),

    url(r'^telechargerDocument/(?P<slug>[\-\d\w]+)$',login_required(views.telechargerDocument), name='telechargerDocument'),

    url(r'^suivre_albums/$', views.suivre_albums, name='suivre_albums'),
    url(r'^suivre_documents/$', views.suivre_documents, name='suivre_documents'),

]
