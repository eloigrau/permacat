from django.test import TestCase, override_settings
from .factories import AlbumFactory


@override_settings(ROOT_URLCONF='photologue.tests.test_urls')
class RequestAlbumTest(TestCase):

    def setUp(self):
        super(RequestAlbumTest, self).setUp()
        self.album = AlbumFactory(slug='test-album')

    def test_archive_album_url_works(self):
        response = self.client.get('/ptests/album/')
        self.assertEqual(response.status_code, 200)

    def test_archive_album_empty(self):
        """If there are no galleries to show, tell the visitor - don't show a
        404."""

        self.album.is_public = False
        self.album.save()

        response = self.client.get('/ptests/album/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['latest'].count(),
                         0)

    def test_paginated_album_url_works(self):
        response = self.client.get('/ptests/albumlist/')
        self.assertEqual(response.status_code, 200)

    def test_album_works(self):
        response = self.client.get('/ptests/album/test-album/')
        self.assertEqual(response.status_code, 200)

    def test_archive_year_album_works(self):
        response = self.client.get('/ptests/album/2011/')
        self.assertEqual(response.status_code, 200)

    def test_archive_month_album_works(self):
        response = self.client.get('/ptests/album/2011/12/')
        self.assertEqual(response.status_code, 200)

    def test_archive_day_album_works(self):
        response = self.client.get('/ptests/album/2011/12/23/')
        self.assertEqual(response.status_code, 200)

    def test_detail_album_works(self):
        response = self.client.get('/ptests/album/2011/12/23/test-album/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_to_list(self):
        """Trivial test - if someone requests the root url of the app
        (i.e. /ptests/'), redirect them to the album list page."""
        response = self.client.get('/ptests/')
        self.assertRedirects(response, '/ptests/album/', 301, 200)
