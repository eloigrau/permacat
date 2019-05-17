# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Article, Commentaire, Projet, CommentaireProjet, Choix
from .forms import ArticleForm, CommentForm, ArticleChangeForm, ProjetForm, ProjetChangeForm, CommentProjetForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import actions, action, models

from django.utils.timezone import now

from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt

@login_required
def forum(request):
    """ Afficher tous les articles de notre blog """
    articles = Article.objects.all().order_by('-date_dernierMessage')  # Nous sélectionnons tous nos articles
    return render(request, 'blog/forum.html', {'derniers_articles': articles})

def acceuil(request):
    return render(request, 'blog/accueil.html')


@login_required
def ajouterNouveauPost(request):
    form = ArticleForm(request.POST or None)
    if form.is_valid():
        article = form.save(request.user)
        url = article.get_absolute_url()
        suffix = "" if article.estPublic else "_permacat"
        action.send(request.user, verb='article_nouveau'+suffix, action_object=article, url=url,
                    description="a ajouté un article : %s" % article.titre)
        return render(request, 'blog/lireArticle.html', {'article': article})
    return render(request, 'blog/ajouterPost.html', { "form": form, })


# @login_required
class ModifierArticle(UpdateView):
    model = Article
    form_class = ArticleChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        url = self.object.get_absolute_url()
        suffix = "_permacat" if self.object.estPublic else ""
        action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                     description="a modifié l'article '%s'" % self.object.titre)
        return HttpResponseRedirect(self.get_success_url())


    def save(self):
        return super(ModifierArticle, self).save()

class SupprimerArticle(DeleteView):
    model = Article
    success_url = reverse_lazy('blog:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])



@login_required
def lireArticle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not article.estPublic and not request.user.is_permacat:
        return render(request, 'notPermacat.html',)

    commentaires = Commentaire.objects.filter(article=article).order_by("date_creation")

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.auteur_comm = request.user
        article.date_dernierMessage = comment.date_creation
        article.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(comment.commentaire))[:96] + "..."
        article.save()
        comment.save()
        url = article.get_absolute_url()
        suffix = "_permacat" if article.estPublic else ""
        action.send(request.user, verb='article_message'+suffix, action_object=article, url=url,
                    description="a réagi à l'article %s" % article.titre)
        return redirect(request.path)

    return render(request, 'blog/lireArticle.html', {'article': article, 'form': form, 'commentaires':commentaires},)


class ListeArticles(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 10

    def get_queryset(self):
        params = dict(self.request.GET.items())

        if "archives" in params and params['archives']:
            qs = Article.objects.filter(estArchive=True)
        else:
            qs = Article.objects.filter(estArchive=False)

        if not self.request.user.is_authenticated or not self.request.user.is_permacat:
            qs = qs.filter(estPublic=True)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "permacat" in params  and self.request.user.is_permacat:
            if params['permacat'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)


        return qs.order_by('-date_dernierMessage', '-date_creation', 'categorie','auteur')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Article.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_annonce if x[0] in cat]
        context['typeFiltre'] = "aucun"
        #context['ordreTriPossibles'] =  ['date dernier message', 'categorie', ]

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        return context



# @login_required
# def ajouterNouveauProjet(request):
#     ModelFormWithFileField
#         if form.is_valid():
#             #simple_upload(request, 'fichier_projet')
#             projet = form.save(request.user)
#             return render(request, 'blog/lireProjet.html', {'projet': projet})
#         return render(request, 'blog/ajouterProjet.html', { "form": form, })

@login_required
def ajouterNouveauProjet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            projet = form.save(request.user)
            url = projet.get_absolute_url()

            suffix = "" if projet.estPublic else "_permacat"
            action.send(request.user, verb='projet_nouveau'+suffix, action_object=projet, url=url,
                    description="a ajouté un projet : '%s'" % projet.titre)
            return render(request, 'blog/lireProjet.html', {'projet': projet})
    else:
        form = ProjetForm(request.POST or None, request.FILES or None)
    return render(request, 'blog/ajouterProjet.html', { "form": form, })

class ModifierProjet(UpdateView):
    model = Projet
    form_class = ProjetChangeForm
    template_name_suffix = '_modifier'
    #fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Projet.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        url = self.object.get_absolute_url()
        suffix = "_permacat" if self.object.estPublic else ""
        action.send(self.request.user, verb='projet_modifier'+suffix, action_object=self.object, url=url,
                     description="a modifié le projet '%s'" % self.object.titre)
        return HttpResponseRedirect(self.get_success_url())

class SupprimerProjet(DeleteView):
    model = Projet
    success_url = reverse_lazy('blog:index_projets')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Projet.objects.get(slug=self.kwargs['slug'])

@login_required
def lireProjet(request, slug):
    projet = get_object_or_404(Projet, slug=slug)

    if not projet.estPublic and not request.user.is_permacat:
        return render(request, 'notPermacat.html',)

    commentaires = CommentaireProjet.objects.filter(projet=projet).order_by("date_creation")

    form = CommentProjetForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.projet = projet
        comment.auteur_comm = request.user
        projet.date_dernierMessage = comment.date_creation
        projet.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(comment.commentaire))[:96] + "..."
        projet.save()
        comment.save()
        url = projet.get_absolute_url()
        suffix = "_permacat" if projet.estPublic else ""
        action.send(request.user, verb='projet_message'+suffix, action_object=projet, url=url,
                    description="a réagit au projet '%s'" % projet.titre)
        return redirect(request.path)

    return render(request, 'blog/lireProjet.html', {'projet': projet, 'form': form, 'commentaires':commentaires},)

class ListeProjets(ListView):
    model = Projet
    context_object_name = "projet_list"
    template_name = "blog/index_projets.html"
    paginate_by = 10

    def get_queryset(self):

        params = dict(self.request.GET.items())

        if "archives" in params and params['archives']:
            qs = Projet.objects.filter(estArchive=True)
        else:
            qs = Projet.objects.filter(estArchive=False)

        if not self.request.user.is_authenticated or not self.request.user.is_permacat:
            qs = qs.filter(estPublic=True)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "permacat" in params and self.request.user.is_permacat:
            if params['permacat'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)

        return qs.order_by('-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Projet.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat = Projet.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_projet if x[0] in cat]
        context['typeFiltre'] = "aucun"
        if 'auteur_id' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        return context


# from django.shortcuts import render
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
#
# def simple_upload(request, nomfichier):
#     if request.method == 'POST' and request.FILES[nomfichier]:
#         myfile = request.FILES[nomfichier]
#         fs = FileSystemStorage()
#         file_path = os.path.join(settings.MEDIA_ROOT, myfile.name)
#         filename = fs.save(file_path, myfile)
#         uploaded_file_url = fs.url(filename)
#         return render(request, 'simple_upload.html', {'uploaded_file_url': uploaded_file_url})
#     return render(request, 'simple_upload.html')


import os
from django.http import HttpResponse, Http404
from django.conf import settings


@login_required
def telecharger_fichier(request):
    path = request.GET['path']
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        mess = "fichier OK"
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        mess = "Fichier introuvable"
    return render(request, 'blog/telechargement.html', {'fichier':file_path, 'message': mess})

#
# def upload(request):
#     if request.POST:
#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return render_to_response('project/upload_successful.html')
#     else:
#         form = FileForm()
#     args = {}
#     args.update(csrf(request))
#     args['form'] = form
#
#     return render_to_response('project/create.html', args)


@login_required
@csrf_exempt
def suivre_projet(request, slug, actor_only=True):
    """
    """
    projet = get_object_or_404(Projet, slug=slug)

    if projet in models.following(request.user):
        actions.unfollow(request.user, projet)
    else:
        actions.follow(request.user, projet, actor_only=actor_only)
    return redirect(projet)


@login_required
@csrf_exempt
def suivre_article(request, slug, actor_only=True):
    """
    """
    article = get_object_or_404(Article, slug=slug)

    if article in models.following(request.user):
        actions.unfollow(request.user, article)
    else:
        actions.follow(request.user, article, actor_only=actor_only)
    return redirect(article)