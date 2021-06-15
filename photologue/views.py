from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, \
    YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .models import Photo, Album, Document
from django.shortcuts import render, redirect
from .forms import PhotoForm, AlbumForm, PhotoChangeForm, AlbumChangeForm, DocumentForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from bourseLibre.constantes import Choix as Choix_global
from bourseLibre.views import testIsMembreAsso

from django.core.exceptions import PermissionDenied
from actstream import actions, action
from django.utils.timezone import now
from bourseLibre.models import Asso
# Album views.


class AlbumListView(ListView):
    paginate_by = 20

    def get_queryset(self):
        qs = Album.objects.on_site()

        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                qs = qs.exclude(asso__abreviation=nomAsso)

        return  qs

class AlbumDetailView(DetailView):
    queryset = Album.objects.on_site()


class AlbumDateView:
    queryset = Album.objects.on_site()
    date_field = 'date_added'
    allow_empty = True


class AlbumDateDetailView(AlbumDateView, DateDetailView):
    pass


class AlbumArchiveIndexView(AlbumDateView, ArchiveIndexView):
    pass


class AlbumDayArchiveView(AlbumDateView, DayArchiveView):
    pass


class AlbumMonthArchiveView(AlbumDateView, MonthArchiveView):
    pass


class AlbumYearArchiveView(AlbumDateView, YearArchiveView):
    make_object_list = True

# Photo views.


class PhotoListView(ListView):
    paginate_by = 20

    def get_queryset(self):
        qs = Photo.objects.on_site()

        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                qs = qs.exclude(albums__asso__abreviation=nomAsso)

        return  qs

class PhotoDetailView(DetailView):
    queryset = Photo.objects.on_site()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['galleries'] = "test"
        return context



class DocListView(ListView):
    paginate_by = 20

    def get_queryset(self):
        qs = Document.objects.all()

        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                qs = qs.exclude(asso__abreviation=nomAsso)

        return qs


class PhotoDateView:
    queryset = Photo.objects.on_site()
    date_field = 'date_added'
    allow_empty = True


class PhotoDateDetailView(PhotoDateView, DateDetailView):
    pass


class PhotoArchiveIndexView(PhotoDateView, ArchiveIndexView):
    pass


class PhotoDayArchiveView(PhotoDateView, DayArchiveView):
    pass


class PhotoMonthArchiveView(PhotoDateView, MonthArchiveView):
    pass


class PhotoYearArchiveView(PhotoDateView, YearArchiveView):
    make_object_list = True


@login_required
def ajouterPhoto(request, albumSlug):
    album = Album.objects.get(slug=albumSlug)
    asso = testIsMembreAsso(request, album.asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    if request.method == 'POST':
        form = PhotoForm(request, request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(request)
            album.photos.add(photo)
            form.save_m2m()
            return redirect(photo.get_absolute_url())
    else:
        form = PhotoForm(request)
    return render(request, 'photologue/photo_ajouter.html', { "form": form, "album":album})



@login_required
def ajouterAlbum(request):
    form = AlbumForm(request, request.POST or None)
    if form.is_valid():
        album = form.save(request)
        #action.send(request.user, verb='album_nouveau', action_object=album, url=album.get_absolute_url(),
         #            description="a ajouté l'album: '%s'" % album.title)
        return redirect(album.get_absolute_url())
    return render(request, 'photologue/album_ajouter.html', { "form": form, })



# @login_required
class ModifierAlbum(UpdateView):
    model = Album
    form_class = AlbumChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Album.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        #self.object.date_modification = now()
        self.object.save()
        #if not self.object.estArchive:
        #    url = self.object.get_absolute_url()
        #    suffix = "_" + self.object.asso.abreviation
        #    action.send(self.request.user, verb='album_modifier'+suffix, action_object=self.object, url=url,
         #                description="a modifié l'album: '%s'" % self.object.titre)
        #envoi_emails_albumouprojet_modifie(self.object, "L'album " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierAlbum, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all()) if self.request.user.estMembre_str(x.abreviation)]

        return form

class SupprimerAlbum(DeleteView):
    model = Album
    success_url = reverse_lazy('photologue:album-list')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Album.objects.get(slug=self.kwargs['slug'])



# @login_required
class ModifierPhoto(UpdateView):
    model = Photo
    form_class = PhotoChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Photo.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        #self.object.date_modification = now()
        self.object.save()
        #if not self.object.estArchive:
        #    url = self.object.get_absolute_url()
        #    suffix = "_" + self.object.asso.abreviation
        #    action.send(self.request.user, verb='photo_modifier'+suffix, action_object=self.object, url=url,
        #                 description="a modifié la photo: '%s'" % self.object.titre)
        #envoi_emails_albumouprojet_modifie(self.object, "L'album " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    #def get_form(self,*args, **kwargs):
    #    form = super(ModifierPhoto, self).get_form(*args, **kwargs)
    #    form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all()) if self.request.user.estMembre_str(x.abreviation)]

        return form

class SupprimerPhoto(DeleteView):
    model = Photo
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Photo.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return self.object.get_album_url()

@login_required
def telechargerDocument(request, slug):
    doc = get_object_or_404(Document, slug=slug)
    return render(doc.get_absolute_url())

@login_required
def ajouterDocument(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request, request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(request)

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse_lazy("photologue:doc-list"))
    else:
        form = DocumentForm(request) # A empty, unbound form

    # Render list page with the documents and the form
    return render(request, 'photologue/document_ajouter.html', { "form": form})



class SupprimerDocument(DeleteView):
    model = Document
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Document.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse_lazy("photologue:doc-list")
