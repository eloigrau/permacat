# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from .models import Article, Commentaire, Choix, Evenement
from .forms import ArticleForm, CommentaireArticleForm, CommentaireArticleChangeForm, ArticleChangeForm, \
     EvenementForm, EvenementArticleForm,accepterParticipationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import actions, action
from actstream.models import followers, following, action_object_stream
from django.utils.timezone import now
from bourseLibre.models import Profil
from django.db.models import Q
from bourseLibre.views_base import DeleteAccess

#from django.contrib.contenttypes.models import ContentType
from bourseLibre.models import Suivis
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin
from hitcount.models import HitCount
from hitcount.views import HitCountMixin


# @login_required
# def forum(request):
#     """ Afficher tous les articles de notre jardinpartage """
#     articles = Article.objects.all().order_by('-date_dernierMessage')  # Nous sélectionnons tous nos articles
#     return render(request, 'jardinpartage/forum.html', {'derniers_articles': articles })

def is_inscrit(user):
    return user.adherent_jp

@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def accueil(request):
    return render(request, 'jardinpartage/accueil.html')


@login_required
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def ajouterArticle(request):
    try:
        form = ArticleForm(request.POST or None)
        if form.is_valid():
            article = form.save(request.user)
            url = article.get_absolute_url()
            #suffix = "_" + article.jardin.nom
            action.send(request.user, verb='article_nouveau', action_object=article, url=url,
                        description="a ajouté un article : (Jardins Partagés) '%s'" % article.titre, type="article_jardin_partage")
            return redirect(article.get_absolute_url())
            #return render(request, 'jardinpartage/lireArticle.html', {'article': article})
    except Exception as inst:
        print(inst)
    return render(request, 'jardinpartage/ajouterPost.html', { "form": form, })


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
        if not self.object.estArchive:
            url = self.object.get_absolute_url()
            action.send(self.request.user, verb='article_modifier', action_object=self.object, url=url,
                         description="a modifié l'article [Jardins Partagés] '%s'" % self.object.titre)

        return HttpResponseRedirect(self.get_success_url())


class SupprimerArticle(DeleteAccess, DeleteView):
    model = Article
    success_url = reverse_lazy('jardinpartage:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])



@login_required
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def lireArticle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not article.est_autorise(request.user):
        return render(request, 'notMembre.html', {'asso':article.asso})

    commentaires = Commentaire.objects.filter(article=article).order_by("date_creation")
    dates = Evenement.objects.filter(article=article).order_by("start_time")

    actions = action_object_stream(article)

    hit_count = HitCount.objects.get_for_object(article)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = CommentaireArticleForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        if comment:
            comment.article = article
            comment.auteur_comm = request.user
            article.date_dernierMessage = comment.date_creation
            article.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
            article.save()
            comment.save()
            url = article.get_absolute_url()+"#idConversation"
            #suffix = "_" + article.asso.nom
            action.send(request.user, verb='article_message', action_object=article, url=url,
                        description="a réagi à l'article: (Jardins Partagés) '%s'" % article.titre, type="article_jardin_partage")
                #envoi_emails_articleouprojet_modifie(article, request.user.username + " a réagit à l'article: " +  article.titre)
        return redirect(request.path)

    return render(request, 'jardinpartage/lireArticle.html', {'article': article, 'form': form, 'commentaires':commentaires, 'dates':dates, 'actions':actions},)

@login_required
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def lireArticle_id(request, id):
    article = get_object_or_404(Article, id=id)
    return lireArticle(request, slug=article.slug)

class ListeArticles(UserPassesTestMixin, ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "jardinpartage/index.html"
    paginate_by = 30

    def test_func(self):
        return is_inscrit(self.request.user)

    def handle_no_permission(self):
        return redirect('jardinpartage:accepter_participation')

    def get_queryset(self):
        params = dict(self.request.GET.items())

        qs = Article.objects.all()

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params and params['categorie'] != "tout":
            qs = qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            if params['ordreTri'] == "-date_dernierMessage":
                qs = qs.filter(date_dernierMessage__isnull=False)
            elif params['ordreTri'] == "-date_modification":
                qs = qs.filter(date_modification__isnull=False)
            elif params['ordreTri'] == "-start_time":
                qs = qs.filter(start_time__isnull=False)
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by( '-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

        self.qs = qs
        return qs.filter(estArchive=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['list_archive'] = self.qs.filter(estArchive=True)
        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Article.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles_jardin")

        context['jardin_list'] = [(x[0], x[1]) for x in Choix.jardins_ptg]

        context['ordreTriPossibles'] = {
                                           "date de création":'-date_creation',
                                           "date du dernier message":'-date_dernierMessage',
                                           "date de la dernière modification":'-date_modification',
                                            "titre": 'titre' }

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET and self.request.GET['categorie'] != "tout":
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                context['categorie_courante'] = ""
        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        return context



class ListeArticles_jardin(ListeArticles):

    def get_queryset(self):
        params = dict(self.request.GET.items())

        qs = Article.objects.all()

        #nom_jardin = [x[1] for x in Choix.jardins_ptg if x[0]==self.kwargs["jardin"]][0]
        if self.kwargs["jardin"] != "0":
            qs = qs.filter(Q(jardin=self.kwargs["jardin"])|Q(jardin="0"))

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params and params['categorie'] != "tout":
            qs = qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by( '-date_creation', '-date_dernierMessage', 'categorie', 'auteur')

        self.qs = qs
        return qs.filter(estArchive=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['list_archive'] = self.qs.filter(estArchive=True)
        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        qs = Article.objects.all()
        if self.kwargs["jardin"] != "0":
            qs = qs.filter(jardin=self.kwargs["jardin"])
        context['auteur_list'] = qs.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat = Article.objects.all().order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]
        context['jardin_list'] = [(x[0], x[1]) for x in Choix.jardins_ptg]
        nom_jardin = [x[1] for x in Choix.jardins_ptg if x[0]==self.kwargs["jardin"]]
        if nom_jardin:
            context['jardin_courant'] = nom_jardin[0]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles")

        context['ordreTriPossibles'] = {
                                           "date de création":'-date_creation',
                                           "date de la dernière modification":'-date_modification',
                                            "titre": 'titre' }

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET and self.request.GET['categorie'] != "tout":
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                context['categorie_courante'] = ""


        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        return context


# @login_required
# def ajouterNouveauProjet(request):
#     ModelFormWithFileField
#         if form.is_valid():
#             #simple_upload(request, 'fichier_projet')
#             projet = form.save(request.user)
#             return render(request, 'jardinpartage/lireProjet.html', {'projet': projet})
#         return render(request, 'jardinpartage/ajouterProjet.html', { "form": form, })




@login_required
@csrf_exempt
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def suivre_article(request, slug, actor_only=True):
    """
    """
    article = get_object_or_404(Article, slug=slug)

    if article in following(request.user):
        actions.unfollow(request.user, article, send_action=False)
    else:
        actions.follow(request.user, article, actor_only=actor_only, send_action=False)
    return redirect(article)

@login_required
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def articles_suivis(request, slug):
    article = Article.objects.get(slug=slug)
    suiveurs = followers(article)
    return render(request, 'jardinpartage/articles_suivis.html', {'suiveurs': suiveurs, "article":article, })


@login_required
def articles_suiveurs(request):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'articles_jardin')
    inscrits = Profil.objects.filter(adherent_jp=True).order_by('username')
    suiveurs = followers(suivi)
    return render(request, 'jardinpartage/articles_suivis.html', {'suiveurs': suiveurs, 'inscrits':inscrits})


@login_required
@csrf_exempt
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def suivre_articles(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_jardin')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('jardinpartage:index')



class ModifierCommentaireArticle(UpdateView):
    model = Commentaire
    form_class = CommentaireArticleChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return Commentaire.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.article.get_absolute_url())


@login_required
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def ajouterEvenement(request, date=None):
    if date:
        form = EvenementForm(request.POST or None, initial={'start_time': date})
    else:
        form = EvenementForm(request.POST or None)

    if form.is_valid():
        form.save(request)
        return redirect('cal:agenda')

    return render(request, 'jardinpartage/ajouterEvenement.html', {'form': form, })



@login_required
@user_passes_test(is_inscrit, login_url='/jardins/accepter_participation')
def ajouterEvenementArticle(request, slug_article):
    form = EvenementArticleForm(request.POST or None)

    if form.is_valid():
        form.save(slug_article)
        return lireArticle_id(request, slug_article)

    return render(request, 'jardinpartage/ajouterEvenement.html', {'form': form, })

def accepter_participation(request):
    form = accepterParticipationForm(request.POST or None)
    if form.is_valid():
        request.user.adherent_jp = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_jardin')
        actions.follow(request.user, suivi, actor_only=True, send_action=False)
        action.send(request.user, verb='inscription_jardins', url=request.user.get_absolute_url(),
                    description="s'est inscrit.e aux jardins partagés", )

        return redirect(reverse('jardinpartage:index'))

    return render(request, 'jardinpartage/accepterParticipation.html', {'form': form, })