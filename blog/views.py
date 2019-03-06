# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
# from django.db.models import Q
from .models import Article, Commentaire
from .forms import ArticleForm, CommentForm, ArticleChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView
#from django.db.models import Q

def accueil(request):
    """ Afficher tous les articles de notre blog """
    articles = Article.objects.all().order_by('-date')  # Nous sélectionnons tous nos articles
    return render(request, 'blog/accueil.html', {'derniers_articles': articles})


@login_required(login_url='/auth/login/')
def ajouterNouveauPost(request):
        form = ArticleForm(request.POST or None)
        if form.is_valid():
            article = form.save(request.user)
            return render(request, 'blog/lireArticle.html', {'article': article})
        return render(request, 'blog/ajouterPost.html', { "form": form, })


# @login_required(login_url='/auth/login/')
class ModifierArticle(UpdateView):
    model = Article
    form_class = ArticleChangeForm
    template_name_suffix = '_modifier'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])

# def index(request):
#     all_posts = Post.objects.all().order_by('-date')
#     template_data = {'posts' : all_posts}
#
#     return render_to_response('index.html', template_data)

# def lire(request,slug):
#
#     article = get_object_or_404(Article, slug=slug)
#     return render(request, 'blog/lire.html', {'article':article})


@login_required(login_url='/auth/login/')
def lireArticle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    commentaires = Commentaire.objects.filter(article=article)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.auteur_comm = request.user
        comment.save()
        return redirect(request.path)

    return render(request, 'blog/lireArticle.html', {'article': article, 'form': form, 'commentaires':commentaires},)



class ListeArticles(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.all()
        params = dict(self.request.GET.items())

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])

        return qs.order_by('categorie', '-date', 'auteur')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Article.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        context['categorie_list'] = Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['typeFiltre'] = "aucun"
        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
        return context

