from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from ..sitemaps import AlbumSitemap, PhotoSitemap

urlpatterns = [
    url(r'^ptests/', include('photologue.urls', namespace='photologue')),
]

sitemaps = {'photologue_galleries': AlbumSitemap,
            'photologue_photos': PhotoSitemap,
            }

urlpatterns += [
    url(r'^sitemap.xml$', sitemap, {'sitemaps': sitemaps}),
]
