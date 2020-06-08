# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from .models import Article, Commentaire, Choix, Evenement
from .forms import ArticleForm, CommentaireArticleForm, CommentaireArticleChangeForm, ArticleChangeForm, \
     EvenementForm, EvenementArticleForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import actions, action
from actstream.models import followers, following, action_object_stream
from django.core.mail import send_mass_mail, mail_admins
from django.utils.timezone import now
from bourseLibre.settings import SERVER_EMAIL

#from django.contrib.contenttypes.models import ContentType
from bourseLibre.models import Suivis
from django.views.decorators.csrf import csrf_exempt
import sys

# @login_required
# def forum(request):
#     """ Afficher tous les articles de notre jardinpartage """
#     articles = Article.objects.all().order_by('-date_dernierMessage')  # Nous sélectionnons tous nos articles
#     return render(request, 'jardinpartage/forum.html', {'derniers_articles': articles })

def accueil(request):
    return render(request, 'jardinpartage/accueil.html')


@login_required
def ajouterArticle(request):
    try:
        form = ArticleForm(request.POST or None)
        if form.is_valid():
            article = form.save(request.user)
            url = article.get_absolute_url()
            suffix = "" if article.estPublic else "_permacat"
            action.send(request.user, verb='article_nouveau'+suffix, action_object=article, url=url,
                        description="a ajouté un article : '%s'" % article.titre)
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
        url = self.object.get_absolute_url()
        suffix = "_permacat" if self.object.estPublic else ""
        action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                     description="a modifié l'article: '%s'" % self.object.titre)
        envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié")
        return HttpResponseRedirect(self.get_success_url())


class SupprimerArticle(DeleteView):
    model = Article
    success_url = reverse_lazy('jardinpartage:index')
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
    dates = Evenement.objects.filter(article=article).order_by("start_time")

    actions = action_object_stream(article)

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
            suffix = "_permacat" if article.estPublic else ""
            action.send(request.user, verb='article_message'+suffix, action_object=article, url=url,
                        description="a réagi à l'article: '%s'" % article.titre)
            envoi_emails_articleouprojet_modifie(article, request.user.username + " a réagit au projet: " +  article.titre)
        return redirect(request.path)

    return render(request, 'jardinpartage/lireArticle.html', {'article': article, 'form': form, 'commentaires':commentaires, 'dates':dates, 'actions':actions},)

@login_required
def lireArticle_id(request, id):
    article = get_object_or_404(Article, id=id)
    return lireArticle(request, slug=article.slug)


class ListeArticles(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "jardinpartage/index.html"
    paginate_by = 30

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

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Article.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="articles_jardin")

        context['ordreTriPossibles'] = {
                                           "date de création":'-date_creation',
                                           "date du dernier message":'-date_dernierMessage',
                                           "date de la dernière modification":'-date_modification',
                                            "titre": 'titre' }

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
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


def envoi_emails_articleouprojet_modifie(articleOuProjet, message):

    titre = "Permacat - Jardin Partagé - Article actualisé" if articleOuProjet else "Permacat - Projet actualisé"
    message =  message +\
              "\n Vous pouvez y accéder en suivant ce lien : http://www.perma.cat" + articleOuProjet.get_absolute_url() + \
              "\n\n------------------------------------------------------------------------------" \
              "\n vous recevez cet email, car vous avez choisi de suivre ce projet sur le site http://www.Perma.Cat/forum/articles/"
   # emails = [(titre, message, SERVER_EMAIL, (suiv.email, )) for suiv in followers(instance)]
    emails = [suiv.email for suiv in followers(articleOuProjet)  if articleOuProjet.auteur != suiv  and (articleOuProjet.estPublic or suiv.is_permacat)]

    if emails:
        try:
            send_mass_mail([(titre, message, SERVER_EMAIL, emails), ])
            #mail_admins("pas d'erreur mails", titre + "\n" + message + "\n xxx \n" + str(emails))
        except:
            mail_admins("erreur", sys.exc_info()[0])



@login_required
@csrf_exempt
def suivre_article(request, slug, actor_only=True):
    """
    """
    article = get_object_or_404(Article, slug=slug)

    if article in following(request.user):
        actions.unfollow(request.user, article)
    else:
        actions.follow(request.user, article, actor_only=actor_only)
    return redirect(article)

@login_required
def articles_suivis(request, slug):
    article = Article.objects.get(slug=slug)
    suiveurs = followers(article)
    return render(request, 'jardinpartage/articles_suivis.html', {'suiveurs': suiveurs, "article":article, })


@login_required
@csrf_exempt
def suivre_articles(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'articles_jardin')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
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
def ajouterEvenement(request, date=None):
    if date:
        form = EvenementForm(request.POST or None, initial={'start_time': date})
    else:
        form = EvenementForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('cal:agenda')

    return render(request, 'jardinpartage/ajouterEvenement.html', {'form': form, })



@login_required
def ajouterEvenementArticle(request, id):
    form = EvenementArticleForm(request.POST or None)

    if form.is_valid():
        form.save(id)
        return lireArticle_id(request, id)

    return render(request, 'jardinpartage/ajouterEvenement.html', {'form': form, })
