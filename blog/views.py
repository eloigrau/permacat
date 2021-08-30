# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from .models import Article, Commentaire, Projet, CommentaireProjet, Choix, Evenement,Asso, AdresseArticle
from .forms import ArticleForm, ArticleAddAlbum, CommentaireArticleForm, CommentaireArticleChangeForm, ArticleChangeForm, ProjetForm, \
    ProjetChangeForm, CommentProjetForm, CommentaireProjetChangeForm, EvenementForm, EvenementArticleForm, AdresseArticleForm
from .filters import ArticleFilter
from.utils import get_suivis_forum
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import actions, action
from actstream.models import followers, following, action_object_stream
from django.utils.timezone import now
from datetime import datetime, timedelta
from bourseLibre.models import Suivis
from bourseLibre.settings import NBMAX_ARTICLES
from bourseLibre.forms import AdresseForm, AdresseForm2
from bourseLibre.constantes import Choix as Choix_global

from bourseLibre.views import testIsMembreAsso
from ateliers.models import Atelier
from photologue.models import Album
from django.views.decorators.csrf import csrf_exempt
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from django.db.models import Q, F
from django.core.exceptions import PermissionDenied
import itertools
# @login_required
# def forum(request):
#     """ Afficher tous les articles de notre blog """
#     articles = Article.objects.all().order_by('-date_dernierMessage')  # Nous sélectionnons tous nos articles
#     return render(request, 'blog/forum.html', {'derniers_articles': articles })

@login_required
def accueil(request):
    cat = Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
    categorie_list = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]
    cat_pc = Article.objects.filter(asso__abreviation="pc").order_by('categorie').values_list('categorie', flat=True).distinct()
    categorie_list_pc = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat_pc]
    cat_rtg = Article.objects.filter(asso__abreviation="rtg").order_by('categorie').values_list('categorie', flat=True).distinct()
    categorie_list_rtg = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat_rtg]
    cat_fer = Article.objects.filter(asso__abreviation="fer").order_by('categorie').values_list('categorie', flat=True).distinct()
    categorie_list_fer = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat_fer]
    cat_gt = Article.objects.filter(asso__abreviation="gt").order_by('categorie').values_list('categorie',
                                                                                                flat=True).distinct()
    categorie_list_gt = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat_gt]

    proj = Projet.objects.filter(estArchive=False, statut='accep').order_by('titre')

    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            proj = proj.exclude(asso__abreviation = nomAsso)

    projets_list = [(x.slug, x.titre, x.get_couleur) for x in proj]

    ateliers = Atelier.objects.filter(start_time__gte=now())

    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            ateliers = ateliers.exclude(asso__abreviation = nomAsso)

    ateliers_list = [(x.slug, x.titre, x.get_couleur) for x in ateliers]
    categorie_list_projets = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce_projets
                                         if x[0] in cat]

    derniers_articles = Article.objects.filter(estArchive=False).order_by('-id')
    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            derniers_articles = derniers_articles.exclude(asso__abreviation=nomAsso)

    derniers_articles_comm = Article.objects.filter(estArchive=False, dernierMessage__isnull=False).order_by('date_dernierMessage')

    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            derniers_articles_comm = derniers_articles_comm.exclude(asso__abreviation=nomAsso)

    derniers_articles_modif = Article.objects.filter(Q(estArchive=False) & Q(date_modification__isnull=False) & ~Q(date_modification=F("date_creation"))).order_by('date_modification')

    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            derniers_articles_modif = derniers_articles_modif.exclude(asso__abreviation=nomAsso)

    derniers = sorted(set([x for x in itertools.chain(derniers_articles_comm[::-1][:8], derniers_articles_modif[::-1][:8], derniers_articles[:8], )]), key=lambda x:x.date_modification if x.date_modification else x.date_creation)[::-1]

    suivis = get_suivis_forum(request)

    return render(request, 'blog/accueil.html', {'categorie_list':categorie_list,'categorie_list_pc':categorie_list_pc,'categorie_list_rtg':categorie_list_rtg,'categorie_list_fer':categorie_list_fer,'categorie_list_gt':categorie_list_gt,'projets_list':projets_list,'ateliers_list':ateliers_list, 'categorie_list_projets':categorie_list_projets,'derniers_articles':derniers, 'suivis':suivis})


@login_required
def ajouterArticle(request):
    form = ArticleForm(request, request.POST or None)
    time_threshold = datetime.now() - timedelta(hours=24)
    articles = Article.objects.filter(auteur=request.user, date_creation__gt=time_threshold)
    if not request.user.is_superuser and len(articles) > NBMAX_ARTICLES:
        return render(request, 'erreur2.html', {"msg": "Vous avez déjà posté %s articles depuis 24h, veuillez patienter un peu avant de poster un nouvel article, merci !"% NBMAX_ARTICLES})

    if form.is_valid():
        article = form.save(request.user)
        url = article.get_absolute_url()
        suffix = "_" + article.asso.abreviation
        action.send(request.user, verb='article_nouveau'+suffix, action_object=article, url=url,
                    description="a ajouté un article : '%s'" % article.titre)
        return redirect(article.get_absolute_url())

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
        self.object.save(sendMail=False)
        if not self.object.estArchive:
            url = self.object.get_absolute_url()
            suffix = "_" + self.object.asso.abreviation
            action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                         description="a modifié l'article (%s): '%s'" %(self.object.asso, self.object.titre))
        #envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierArticle, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all().order_by('nom')) if self.request.user.estMembre_str(x.abreviation)]
        form.fields["album"].choices = [("", "---------")] + [(x.id, x.title) for i, x in enumerate(Album.objects.all().order_by('title')) if self.request.user.estMembre_str(x.asso.abreviation)]

        return form

# @login_required
class ArticleAddAlbum(UpdateView):
    model = Article
    form_class = ArticleAddAlbum
    template_name_suffix = '_ajouteralbum'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save(sendMail=False)
        if not self.object.estArchive:
            url = self.object.get_absolute_url()
            suffix = "_" + self.object.asso.abreviation
            action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                         description="a associé un album à l'article: '%s'" % self.object.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ArticleAddAlbum, self).get_form(*args, **kwargs)
        form.fields["album"].choices = [("", "---------")] + [(x.id, x.title) for i, x in enumerate(Album.objects.all().order_by('title')) if self.request.user.estMembre_str(x.asso.abreviation)]

        return form

@login_required
def articleSupprimerAlbum(request, slug):
    art = Article.objects.get(slug=slug)
    art.album = None
    art.save()
    return redirect(art.get_absolute_url())


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
    ateliers = Atelier.objects.filter(article=article).order_by('-start_time')
    lieux = AdresseArticle.objects.filter(article=article).order_by('titre')

    if not article.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso": str(article.asso)})

    commentaires = Commentaire.objects.filter(article=article).order_by("date_creation")
    dates = Evenement.objects.filter(article=article).order_by("-start_time")

    actions = action_object_stream(article)
    hit_count = HitCount.objects.get_for_object(article)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = CommentaireArticleForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        from datetime import datetime, timedelta
        import pytz
        utc = pytz.UTC
        date_limite = utc.localize(datetime.today() - timedelta(hours=1))
        if comment and not Commentaire.objects.filter(commentaire=comment.commentaire, article=article, date_creation__gt=date_limite):
            comment.article = article
            comment.auteur_comm = request.user
            article.date_dernierMessage = now()
            article.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96]
            if len(("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))) > 96:
                article.dernierMessage += "..."

            article.save(sendMail=False)
            comment.save()
            url = article.get_absolute_url()+"#idConversation"
            suffix = "_" + article.asso.abreviation
            action.send(request.user, verb='article_message'+suffix, action_object=article, url=url,
                        description="a réagi à l'article: '%s'" % article.titre)
            #envoi_emails_articleouprojet_modifie(article, request.user.username + " a réagit au projet: " +  article.titre, True)
        return redirect(request.path)

    return render(request, 'blog/lireArticle.html', {'article': article, 'form': form, 'commentaires':commentaires, 'dates':dates, 'actions':actions, 'ateliers':ateliers, 'lieux':lieux},)

@login_required
def lireArticle_id(request, id):
    article = get_object_or_404(Article, id=id)
    return lireArticle(request, slug=article.slug)


class ListeArticles(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())

        qs = Article.objects.filter(estArchive=False)

        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__nom="public")
        else:
            for nomAsso in Choix_global.abreviationsAsso:
                if not getattr(self.request.user, "adherent_" + nomAsso):
                    qs = qs.exclude(asso__abreviation=nomAsso)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "permacat" in params and self.request.user.adherent_pc:
            if params['permacat'] == "True":
                qs = qs.filter(asso_abreviation="pc")
            else:
                qs = qs.filter(estPublic=True)

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

        self.qs = qs
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['list_archive'] = Article.objects.filter(estArchive=True)
        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        #context['auteur_list'] = Article.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat = Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]

        for nomAsso in Choix_global.abreviationsAsso:
            if getattr(self.request.user, "adherent_" + nomAsso):
                cat = Article.objects.filter(asso__abreviation=nomAsso).order_by('categorie').values_list('categorie', flat=True).distinct()
                context['categorie_list_'+nomAsso] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]

        proj = Projet.objects.filter(estArchive=False)
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                proj = proj.exclude(asso__abreviation=nomAsso)
        cat = proj.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list_projet'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce_projets if
                                            x[0] in cat]

        context['projets_list'] = [(x.slug, x.titre, x.get_couleur) for x in proj]

        context['typeFiltre'] = "aucun"

        context['suivis'] = get_suivis_forum(self.request)
        context['ordreTriPossibles'] = Choix.ordre_tri_articles

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                try:
                    context['categorie_courante'] = [x[1] for x in Choix.type_annonce_projets if x[0] == self.request.GET['categorie']][0]
                except:
                    try:
                        projet = Projet.objects.get(slug=self.request.GET['categorie'])
                        context['categorie_courante'] = "Projet : " + projet.titre
                    except:
                        context['categorie_courante'] = "Catégorie inconnue : " + self.request.GET['categorie']

        assos= Asso.objects.all()
        context['asso_list'] = [(x.nom, x.abreviation) for x in assos]
        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['ordre_triage'] = list(Choix.ordre_tri_articles.keys())[list(Choix.ordre_tri_articles.values()).index(self.request.GET['ordreTri'])]
        else:
            context['ordre_triage'] = "date du dernier message"
        return context


class ListeArticles_asso(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        nom_asso = self.kwargs['asso']
        asso = testIsMembreAsso(self.request, nom_asso)
        if not isinstance(asso, Asso):
            raise PermissionDenied

        qs = Article.objects.all()

        if asso.abreviation == "public":
            qs = qs.exclude(Q(asso__abreviation="pc")|Q(asso__abreviation="rtg")|Q(asso__abreviation="fer")|Q(asso__abreviation="gt")|Q(asso__abreviation="scic")|Q(asso__abreviation="citealt"))
        else:
            qs = qs.filter(asso__abreviation=asso.abreviation)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "permacat" in params  and self.request.user.adherent_pc:
            if params['permacat'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_creation', '-date_dernierMessage', 'categorie', 'auteur')

        self.qs = qs
        return qs.filter(estArchive=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['list_archive'] = self.qs.filter(estArchive=True)
        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Article.objects.all().order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat= Article.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]
        context['categorie_list_projets'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce_projets
                                             if x[0] in cat]

        if self.kwargs['asso']:
            assos= Asso.objects.all()
            nom_asso = self.kwargs['asso']
            asso = testIsMembreAsso(self.request, nom_asso)
            if not isinstance(asso, Asso):
                raise PermissionDenied

        for nomAsso in Choix_global.abreviationsAsso:
            if getattr(self.request.user, "adherent_" + nomAsso):
                cat = Article.objects.filter(asso__abreviation=nomAsso).order_by('categorie').values_list('categorie', flat=True).distinct()
                context['categorie_list_'+nomAsso] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.type_annonce if x[0] in cat]

        proj = Projet.objects.filter(estArchive=False)
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                proj = proj.exclude(asso__abreviation=nomAsso)

        context['projets_list'] = [(x.slug, x.titre, x.get_couleur) for x in proj]
        #
        # ateliers = Atelier.objects.filter(start_time__gte=now())
        # if not self.request.user.adherent_pc:
        #     ateliers = ateliers.exclude(asso__abreviation="pc")
        # if not self.request.user.adherent_fer:
        #     ateliers = ateliers.exclude(asso__abreviation="fer")
        # if not self.request.user.adherent_rtg:
        #     ateliers = ateliers.exclude(asso__abreviation="rtg")
        # context['ateliers_list'] = [(x.slug, x.titre, x.get_couleur) for x in ateliers]

        context['asso_list'] = [(x.nom, x.abreviation) for x in assos]
        context['asso_courante'] = asso
        context['typeFiltre'] = "aucun"
        context['suivis'] = get_suivis_forum(self.request)


        context['ordreTriPossibles'] = Choix.ordre_tri_articles

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                try:
                    context['categorie_courante'] = [x[1] for x in Choix.type_annonce_projets if x[0] == self.request.GET['categorie']][0]
                except:
                    context['categorie_courante'] = ""

        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['ordre_triage'] = list(Choix.ordre_tri_articles.keys())[list(Choix.ordre_tri_articles.values()).index(self.request.GET['ordreTri'])]
        else:
            context['ordre_triage'] = "date du dernier message"

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
        form = ProjetForm(request, request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            projet = form.save(request.user)
            url = projet.get_absolute_url()

            suffix = "_" + projet.asso.abreviation
            action.send(request.user, verb='projet_nouveau'+suffix, action_object=projet, url=url,
                    description="a ajouté un projet : '%s'" % projet.titre)
            return redirect(url)

    else:
        form = ProjetForm(request, request.POST or None, request.FILES or None, )
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
        if not self.object.estArchive:
            url = self.object.get_absolute_url()
            suffix = "_" + self.object.asso.abreviation
            action.send(self.request.user, verb='projet_modifier'+suffix, action_object=self.object, url=url,
                         description="a modifié le projet: '%s'" % self.object.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "Le projet " +  self.object.titre + "a été modifié", False)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierProjet, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all()) if self.request.user.estMembre_str(x.abreviation)]
        return form

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

    if not projet.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso":"Permacat"})

    commentaires = CommentaireProjet.objects.filter(projet=projet).order_by("date_creation")
    actions = action_object_stream(projet)

    form = CommentProjetForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.projet = projet
        comment.auteur_comm = request.user
        projet.date_dernierMessage = comment.date_creation
        projet.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
        projet.save(sendMail=False)
        comment.save()
        url = projet.get_absolute_url()+"#idConversation"
        suffix = "_" + projet.asso.abreviation
        action.send(request.user, verb='projet_message'+suffix, action_object=projet, url=url,
                    description="a réagit au projet: '%s'" % projet.titre)
        #envoi_emails_articleouprojet_modifie(projet, request.user.username + " a réagit au projet: " +  projet.titre, False)
        return redirect(request.path)

    return render(request, 'blog/lireProjet.html', {'projet': projet, 'form': form, 'commentaires':commentaires, 'actions':actions},)

class ListeProjets(ListView):
    model = Projet
    context_object_name = "projet_list"
    template_name = "blog/index_projets.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())

        qs = Projet.objects.all()

        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__abreviation="public")
        else:
            for nomAsso in Choix_global.abreviationsAsso:
                if not getattr(self.request.user, "adherent_" + nomAsso):
                    qs = qs.exclude(asso__abreviation=nomAsso)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "statut" in params:
            qs = qs.filter(statut=params['statut'])

        if "permacat" in params and self.request.user.adherent_pc:
            if params['permacat'] == "True":
                qs = qs.filter(estPublic=False)
            else:
                qs = qs.filter(estPublic=True)

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_dernierMessage', '-date_creation', 'categorie', 'auteur')

        self.qs = qs
        return qs.filter(estArchive=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['list_archive'] = self.qs.filter(estArchive=True)
        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Projet.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat = Projet.objects.all().order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_projet if x[0] in cat]
        cat = Projet.objects.all().order_by('statut').values_list('statut', flat=True).distinct()
        context['statut_list'] = [x for x in Choix.statut_projet if x[0] in cat]
        context['typeFiltre'] = "aucun"

        context['ordreTriPossibles'] = Choix.ordre_tri_projets

        if 'auteur_id' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_projet if x[0] == self.request.GET['categorie']][0]
            except:
                context['categorie_courante'] = ""
        if 'statut' in self.request.GET:
            context['typeFiltre'] = "statut"
            try:
                context['statut_courant'] = [x[1] for x in Choix.statut_projet if x[0] == self.request.GET['statut']][0]
            except:
                context['statut_courant'] = ""
        if 'permacat' in self.request.GET:
            context['typeFiltre'] = "permacat"
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        # if 'ordreTri' in self.request.GET:
        #     context['typeFiltre'] = "ordreTri"
        #     context['ordre_triage'] = list(Choix.ordre_tri_projets.keys())[list(Choix.ordre_tri_projets.values()).index(self.request.GET['ordreTri'])]
        # else:
        #     context['ordre_tries'] = False
        #     context['ordre_triage'] = "date du dernier message"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="projets")
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

    if projet in following(request.user):
        actions.unfollow(request.user, projet, send_action=False)
    else:
        actions.follow(request.user, projet, actor_only=actor_only, send_action=False)
    return redirect(projet)


@login_required
@csrf_exempt
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
def projets_suivis(request, slug):
    projet = Projet.objects.get(slug=slug)
    suiveurs = followers(projet)
    return render(request, "blog/projets_suivis.html", {'suiveurs': suiveurs, "projet":projet})

@login_required
def articles_suivis(request, slug):
    article = Article.objects.get(slug=slug)
    suiveurs = followers(article)
    return render(request, 'blog/articles_suivis.html', {'suiveurs': suiveurs, "article":article, })

@login_required
def articles_suiveurs(request, asso_abreviation='punlic'):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_'+ str(asso_abreviation))
    suiveurs = sorted(followers(suivi), key= lambda x: str.lower(x.username))
    return render(request, 'blog/articles_suivis.html', {'suiveurs': suiveurs, })


@login_required
@csrf_exempt
def suivre_articles(request, asso_abreviation='public', actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(asso_abreviation))

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('blog:acceuil')

@login_required
@csrf_exempt
def suivre_projets(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('blog:index_projets')



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


class ModifierCommentaireProjet(UpdateView):
    model = CommentaireProjet
    form_class = CommentaireProjetChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return CommentaireProjet.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.projet.get_absolute_url())


@login_required
def ajouterEvenement(request, date=None):
    if date:
        form = EvenementForm(request.POST or None, initial={'start_time': date})
    else:
        form = EvenementForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('cal:agenda')

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })



@login_required
def ajouterEvenementArticle(request, id_article):
    form = EvenementArticleForm(request.POST or None)

    if form.is_valid():
        form.save(id_article)
        return lireArticle_id(request, id_article)

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })


class SupprimerEvenementArticle(DeleteView):
    model = AdresseArticle
    success_url = reverse_lazy('blog:index')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return AdresseArticle.objects.get(id=self.kwargs['id_evenementArticle'])

    def get_success_url(self):
        return Article.objects.get(slug=self.kwargs['slug_article']).get_absolute_url()

@login_required
def ajouterAdresseArticle(request, id_article):
    article = Article.objects.get(id=id_article)
    form = AdresseArticleForm(request.POST or None)
    form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm2(request.POST or None)

    if form.is_valid() and (form_adresse.is_valid() or form_adresse2.is_valid()):
        if 'adressebtn' in request.POST:
            adresse = form_adresse.save()
        else:
            adresse = form_adresse2.save()
        form.save(article, adresse)
        return lireArticle_id(request, id_article)

    return render(request, 'blog/ajouterAdresse.html', {'article':article, 'form': form, 'form_adresse':form_adresse, 'form_adresse2':form_adresse2 })


class SupprimerAdresseArticle(DeleteView):
    model = AdresseArticle
    success_url = reverse_lazy('blog:index')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return AdresseArticle.objects.get(id=self.kwargs['id_adresse'])

    def get_success_url(self):
        return Article.objects.get(slug=self.kwargs['slug_article']).get_absolute_url()

@login_required
def voirCarteLieux(request, id_article):
    article = Article.objects.get(id=id_article)
    lieux = article.getLieux()
    titre = "Lieux associés à l'article '" + str(article.titre) +"'"
    return render(request, 'blog/carte_lieux.html', {'titre':titre, "lieux":lieux})



@login_required
def supprimerAtelierArticle(request, article_slug, atelier_slug):
    atelier = Atelier.objects.get(slug=atelier_slug)
    atelier.article = None
    atelier.save()

    return lireArticle(request, article_slug)

# methode pour migrer les donnees
def changerArticles_jardin(request):
    from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
    articles = Article.objects.filter(categorie="Jardin")
    for article in articles:
        new_art = Art_jardin.objects.create(categorie='Discu',
                                titre = article.titre,
                                auteur = article.auteur,
                                slug = article.slug,
                                contenu = article.contenu,
                                date_creation = article.date_creation,
                                date_modification = article.date_modification,
                                estPublic = article.estPublic,
                                estModifiable = article.estModifiable,
                            
                                date_dernierMessage = article.date_dernierMessage,
                                dernierMessage = article.dernierMessage,
                                estArchive = article.estArchive,)
        commentaires = Commentaire.objects.filter(article=article)
        for commentaire in commentaires:
            new = Comm_jardin.objects.create(auteur_comm = commentaire.auteur_comm, commentaire = commentaire.commentaire,
                                     article = new_art, date_creation= commentaire.date_creation)
        article.delete()

    return render(request, 'blog/accueil.html')



@login_required
def filtrer_articles(request):
    articles_list = Article.objects.all()
    for nomAsso in Choix_global.abreviationsAsso:
        if not getattr(request.user, "adherent_" + nomAsso):
            articles_list = articles_list.exclude(asso__abreviation=nomAsso)
    f = ArticleFilter(request.GET, queryset=articles_list)

    return render(request, 'blog/article_filter.html', {'filter': f})



