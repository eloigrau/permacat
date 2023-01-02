import zipfile
from zipfile import BadZipFile
import logging
import os
from io import BytesIO

from PIL import Image


from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.encoding import force_text
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.forms import ClearableFileInput
from django.template.defaultfilters import filesizeformat

from .models import Album, Photo, Document
from bourseLibre.models import Asso
from blog.models import Article
from django_summernote.widgets import SummernoteWidget
from django.utils.text import slugify
import itertools

logger = logging.getLogger('photologue.forms')




class UploadZipForm(forms.Form):
    zip_file = forms.FileField()

    title = forms.CharField(label=_('Title'),
                            max_length=250,
                            required=False,
                            help_text=_('All uploaded photos will be given a title made up of this title + a '
                                        'sequential number.<br>This field is required if creating a new '
                                        'album, but is optional when adding to an existing album - if '
                                        'not supplied, the photo titles will be creating from the existing '
                                        'album name.'))
    album = forms.ModelChoiceField(Album.objects.all(),
                                     label=_('Album'),
                                     required=False,
                                     help_text=_('Select a album to add these images to. Leave this empty to '
                                                 'create a new album from the supplied title.'))
    caption = forms.CharField(label=_('Caption'),
                              required=False,
                              help_text=_('Caption will be added to all photos.'))
    description = forms.CharField(label=_('Description'),
                                  required=False,
                                  help_text=_('A description of this Album. Only required for new galleries.'))



    def clean_zip_file(self):
        """Open the zip file a first time, to check that it is a valid zip archive.
        We'll open it again in a moment, so we have some duplication, but let's focus
        on keeping the code easier to read!
        """
        zip_file = self.cleaned_data['zip_file']
        try:
            zip = zipfile.ZipFile(zip_file)
        except BadZipFile as e:
            raise forms.ValidationError(str(e))
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            raise forms.ValidationError('"%s" in the .zip archive is corrupt.' % bad_file)
        zip.close()  # Close file in all cases.
        return zip_file

    def clean_title(self):
        title = self.cleaned_data['title']
        if title and Album.objects.filter(title=title).exists():
            raise forms.ValidationError(_('A album with that title already exists.'))
        return title

    def clean(self):
        cleaned_data = super().clean()
        if not self['title'].errors:
            # If there's already an error in the title, no need to add another
            # error related to the same field.
            if not cleaned_data.get('title', None) and not cleaned_data['album']:
                raise forms.ValidationError(
                    _('Select an existing album, or enter a title for a new album.'))
        return cleaned_data

    def save(self, request=None, zip_file=None):
        if not zip_file:
            zip_file = self.cleaned_data['zip_file']
        zip = zipfile.ZipFile(zip_file)
        count = 1
        current_site = Site.objects.get(id=settings.SITE_ID)
        if self.cleaned_data['album']:
            logger.debug('Using pre-existing album.')
            album = self.cleaned_data['album']
        else:
            logger.debug(
                force_text('Creating new album "{0}".').format(self.cleaned_data['title']))
            album = Album.objects.create(title=self.cleaned_data['title'],
                                             slug=slugify(self.cleaned_data['title']),
                                             description=self.cleaned_data['description'],
                                             asso=self.cleaned_data['asso'])
            album.sites.add(current_site)
        for filename in sorted(zip.namelist()):

            logger.debug('Reading file "{}".'.format(filename))

            if filename.startswith('__') or filename.startswith('.'):
                logger.debug('Ignoring file "{}".'.format(filename))
                continue

            if os.path.dirname(filename):
                logger.warning('Ignoring file "{}" as it is in a subfolder; all images should be in the top '
                               'folder of the zip.'.format(filename))
                if request:
                    messages.warning(request,
                                     _('Ignoring file "{filename}" as it is in a subfolder; all images should '
                                       'be in the top folder of the zip.').format(filename=filename),
                                     fail_silently=True)
                continue

            data = zip.read(filename)

            if not len(data):
                logger.debug('File "{}" is empty.'.format(filename))
                continue

            photo_title_root = self.cleaned_data['title'] if self.cleaned_data['title'] else album.title

            # A photo might already exist with the same slug. So it's somewhat inefficient,
            # but we loop until we find a slug that's available.
            while True:
                photo_title = ' '.join([photo_title_root, str(count)])
                slug = slugify(photo_title)
                if Photo.objects.filter(slug=slug).exists():
                    count += 1
                    continue
                break

            photo = Photo(title=photo_title,
                          slug=slug,
                          caption=self.cleaned_data['caption'],
                          asso=self.cleaned_data['asso'])

            # Basic check that we have a valid image.
            try:
                file = BytesIO(data)
                opened = Image.open(file)
                opened.verify()
            except Exception:
                # Pillow doesn't recognize it as an image.
                # If a "bad" file is found we just skip it.
                # But we do flag this both in the logs and to the user.
                logger.error('Could not process file "{}" in the .zip archive.'.format(
                    filename))
                if request:
                    messages.warning(request,
                                     _('Could not process file "{0}" in the .zip archive.').format(
                                         filename),
                                     fail_silently=True)
                continue

            contentfile = ContentFile(data)
            photo.image.save(filename, contentfile)
            photo.save()
            photo.sites.add(current_site)
            album.photos.add(photo)
            count += 1

        zip.close()

        if request:
            messages.success(request,
                             _('The photos have been added to album "{0}".').format(
                                 album.title),
                             fail_silently=True)


class AlbumForm(forms.ModelForm):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                              label="Album public ou réservé aux adhérents de l'asso :", )
    article = forms.ModelChoiceField(queryset=Article.objects.all(), required=False, empty_label=True,
                              label="Associer l'album à un article du forum ?",)

    class Meta:
        model = Album
        fields = ['asso', 'title', 'description', 'tags', 'article', 'estModifiable', ]
        widgets = {
            'caption': SummernoteWidget(),
        }

    def save(self, request):
        instance = super(AlbumForm, self).save(commit=False)
        max_length = Photo._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.title)[:max_length]

        for x in itertools.count(1):
            if not Album.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = request.user
        instance.save()

        if self.cleaned_data['article']:
            art = Article.objects.get(titre=self.cleaned_data['article'])
            art.album = instance
            art.save()

        return instance

    def __init__(self, request, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all() if request.user.estMembre_str(x.abreviation)]
        self.fields["article"].choices = [('', '(non)')] + [(x.id, x.titre) for i, x in enumerate(Article.objects.filter(estArchive=False).order_by('titre')) if request.user.estMembre_str(x.asso.abreviation)]


class AlbumChangeForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['asso', 'title', 'description',  'tags', 'estModifiable',]
        widgets = {
            'description': SummernoteWidget(),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'title', 'caption']
        widgets = {
            'caption': SummernoteWidget(),
            'image': ClearableFileInput(attrs={'multiple': True}),
        }

    def clean_content(self):
        content = self.cleaned_data['image']
        if content._size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (
            filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        return content

    def __init__(self, request, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
     #   self.fields["asso"].choices = sorted([(x.id, x.nom) for x in Asso.objects.all() if request.user.estMembre_str(x.abreviation)], key=lambda x:x[0])

    def save(self, request, commit=True):
        instance = super(PhotoForm, self).save(commit=False)
        return instance


class PhotoChangeForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = [ 'title', 'caption', 'tags']
        widgets = {
            'caption': SummernoteWidget(),
        }


class DocumentAssocierArticleForm(forms.Form):
    article = forms.ModelChoiceField(queryset=Article.objects.all().order_by('titre'), required=True,
                              label="Document public ou réservé aux adhérents de l'asso :", )

class DocumentForm(forms.ModelForm):
    doc = forms.FileField(
        label='Choisir un fichier',
        help_text='max. 20 megabytes'
    )

    asso = forms.ModelChoiceField(queryset=Asso.objects.all(), required=True,
                              label="Document public ou réservé aux adhérents de l'asso :", )

    class Meta:
        model = Document
        fields = ['asso', 'titre', 'doc', 'tags']

    def __init__(self, request, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if request.user.estMembre_str(x.abreviation)]

    def save(self, request, article, commit=True):
        instance = super(DocumentForm, self).save(commit=False)
        max_length = Photo._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Photo.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = request.user
        if article:
            instance.article = article

        if commit:
            instance.save()


        return instance