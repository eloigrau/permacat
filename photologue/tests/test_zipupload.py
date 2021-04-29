import copy

from django.test import TestCase
from django.contrib.auth.models import User
from django import VERSION

from ..models import Album, Photo
from .factories import AlbumFactory, PhotoFactory, SAMPLE_ZIP_PATH, SAMPLE_NOT_IMAGE_ZIP_PATH, \
    IGNORED_FILES_ZIP_PATH, LANDSCAPE_IMAGE_PATH


class AlbumUploadTest(TestCase):

    """Testing the admin page that allows users to upload zips."""

    def setUp(self):
        super(AlbumUploadTest, self).setUp()
        user = User.objects.create_user('john.doe',
                                        'john.doe@example.com',
                                        'secret')
        user.is_staff = True
        user.save()
        self.assertTrue(self.client.login(username='john.doe', password='secret'))

        self.zip_file = open(SAMPLE_ZIP_PATH, mode='rb')

        self.sample_form_data = {'zip_file': self.zip_file,
                                 'title': 'This is a test title'}

    def tearDown(self):
        super(AlbumUploadTest, self).tearDown()
        self.zip_file.close()
        for photo in Photo.objects.all():
            photo.delete()

    def test_get(self):
        """We can get the custom admin page."""

        response = self.client.get('/admin/photologue/photo/upload_zip/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/photologue/photo/upload_zip.html')

        self.assertContains(response, 'Upload a zip archive of photos')

    def test_breadcrumbs(self):
        """Quick check that the breadcrumbs are generated correctly."""

        response = self.client.get('/admin/photologue/photo/upload_zip/')
        self.assertContains(
            response, """<div class="breadcrumbs"><a href="/admin/">Home</a> &rsaquo;
            <a href="/admin/photologue/">Photologue</a> &rsaquo; Photos &rsaquo; Upload </div>""", html=True)

    def test_missing_fields(self):
        """Missing fields mean the form is redisplayed with errors."""

        test_data = copy.copy(self.sample_form_data)
        del test_data['zip_file']
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_good_data(self):
        """Upload a zip with a single file it it: 'sample.jpg'.
        It gets assigned to a newly created album 'Test'."""

        test_data = copy.copy(self.sample_form_data)
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        # The redirect Location has changed in Django 1.9 - it used to be an absolute URI, now it returns
        # a relative one.
        if VERSION[0] == 1 and VERSION[1] <= 8:
            location = 'http://testserver/admin/photologue/photo/'
        else:
            location = '..'

        self.assertEqual(response['Location'], location)

        self.assertQuerysetEqual(Album.objects.all(),
                                 ['<Album: This is a test title>'])
        self.assertQuerysetEqual(Photo.objects.all(),
                                 ['<Photo: This is a test title 1>'])

        # The photo is attached to the album.
        album = Album.objects.get(title='This is a test title')
        self.assertQuerysetEqual(album.photos.all(),
                                 ['<Photo: This is a test title 1>'])

    def test_duplicate_album(self):
        """If we try to create a Album with a title that duplicates an existing title, refuse to load."""

        AlbumFactory(title='This is a test title')

        test_data = copy.copy(self.sample_form_data)
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form']['title'].errors)

    def test_title_or_album(self):
        """We should supply either a title field or a album."""

        test_data = copy.copy(self.sample_form_data)
        del test_data['title']
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        self.assertEqual(list(response.context['form'].non_field_errors()),
                         ['Select an existing album, or enter a title for a new album.'])

    def test_not_image(self):
        """A zip with a file of the wrong format (.txt).
        That file gets ignored."""

        test_data = copy.copy(self.sample_form_data)
        with open(SAMPLE_NOT_IMAGE_ZIP_PATH, mode='rb') as f:
            test_data['zip_file'] = f
            response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
            self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(Album.objects.all(),
                                 ['<Album: This is a test title>'])
        self.assertQuerysetEqual(Photo.objects.all(),
                                 ['<Photo: This is a test title 1>'])

    def test_ignored(self):
        """Ignore anything that does not look like a image file.
        E.g. hidden files, and folders.
        We have two images: one in the top level of the zip, and one in a subfolder.
        The second one gets ignored - we only process files at the zip root."""

        test_data = copy.copy(self.sample_form_data)
        with open(IGNORED_FILES_ZIP_PATH, mode='rb') as f:
            test_data['zip_file'] = f
            response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
            self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(Album.objects.all(),
                                 ['<Album: This is a test title>'])
        self.assertQuerysetEqual(Photo.objects.all(),
                                 ['<Photo: This is a test title 1>'])

    def test_existing_album(self):
        """Add the photos in the zip to an existing album."""

        existing_album = AlbumFactory(title='Existing')

        test_data = copy.copy(self.sample_form_data)
        test_data['album'] = existing_album.id
        del test_data['title']
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(Album.objects.all(),
                                 ['<Album: Existing>'])
        self.assertQuerysetEqual(Photo.objects.all(),
                                 ['<Photo: Existing 1>'])

        # The photo is attached to the existing album.
        self.assertQuerysetEqual(existing_album.photos.all(),
                                 ['<Photo: Existing 1>'])

    def test_existing_album_custom_title(self):
        """Add the photos in the zip to an existing album, but specify a
        custom title for the photos."""

        existing_album = AlbumFactory(title='Existing')

        test_data = copy.copy(self.sample_form_data)
        test_data['album'] = existing_album.id
        test_data['title'] = 'Custom title'
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(Photo.objects.all(),
                                 ['<Photo: Custom title 1>'])

    def test_duplicate_slug(self):
        """Uploading a zip, but a photo already exists with the target slug."""

        PhotoFactory(title='This is a test title 1')
        PhotoFactory(title='This is a test title 2')

        test_data = copy.copy(self.sample_form_data)
        response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(Photo.objects.all(),
                                 [
                                 '<Photo: This is a test title 1>',
                                 '<Photo: This is a test title 2>',
                                 '<Photo: This is a test title 3>'
                                 ],
                                 ordered=False)

    def test_bad_zip(self):
        """Supplied file is not a zip file - tell user."""

        test_data = copy.copy(self.sample_form_data)
        with open(LANDSCAPE_IMAGE_PATH, mode='rb') as f:
            test_data['zip_file'] = f
            response = self.client.post('/admin/photologue/photo/upload_zip/', test_data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form']['zip_file'].errors)
