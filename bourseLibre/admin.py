# -*- coding: utf-8 -*-
from .models import  Adresse, Produit, Panier, Item, Adhesion_permacat, Asso, MessageGeneral, Conversation, InscriptionNewsletter, InvitationDansSalon, InscritSalon
from blog.models import Article, Projet, FicheProjet, Commentaire, Discussion, CommentaireProjet, Evenement, EvenementAcceuil, AdresseArticle
from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
from fiches.models import Fiche, Atelier as atelier_fiche, CommentaireFiche
from ateliers.models import Atelier, CommentaireAtelier, InscriptionAtelier
from agoratransition.models import InscriptionExposant, Proposition, Message_agora
from django.contrib.admin.models import LogEntry


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProducteurChangeForm_admin
from .models import Profil, Salon
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    form = ProducteurChangeForm_admin
    model = Profil
    list_display = ['id','username',  'last_login', 'email', 'date_notifications',
                    'inscrit_newsletter', 'accepter_annuaire', 'isCotisationAJour_pc' ]

    readonly_fields = ('date_registration','last_login','adresse')

    fieldsets = (
        (None, {'fields': ('username','description','competences','pseudo_june', 'adherent_pc', 'adherent_rtg','adherent_fer', 'adherent_scic', 'adherent_citealt','adherent_viure','adherent_bzz2022','adresse', 'inscrit_newsletter', 'adherent_jp', 'date_notifications','accepter_annuaire', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )


class ArticleAdmin(admin.ModelAdmin):
        list_display = ('titre', 'asso', 'categorie', 'estArchive', 'get_partagesAssotxt' )
class Article_jardinAdmin(admin.ModelAdmin):
        list_display = ('titre', 'jardin', 'categorie', 'estArchive', )
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'estArchive', 'ficheprojet')
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'categorie', 'estUneOffre', 'asso', 'unite_prix')
class Adhesion_permacatAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_cotisation', 'montant')
class AssoAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(Article, ArticleAdmin)
admin.site.register(Art_jardin, Article_jardinAdmin)
admin.site.register(Evenement)
admin.site.register(EvenementAcceuil)
admin.site.register(AdresseArticle)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(FicheProjet)
admin.site.register(Profil, CustomUserAdmin)

admin.site.register(Adresse)
admin.site.register(Asso, AssoAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Panier)
admin.site.register(Item)
admin.site.register(MessageGeneral)
admin.site.register(InscriptionNewsletter)
admin.site.register(Adhesion_permacat, Adhesion_permacatAdmin)

admin.site.register(Conversation)
admin.site.register(Commentaire)
admin.site.register(Discussion)
admin.site.register(Comm_jardin)
admin.site.register(CommentaireProjet)

admin.site.register(Fiche)
admin.site.register(CommentaireFiche)
admin.site.register(atelier_fiche)

admin.site.register(LogEntry)

admin.site.register(Atelier)
admin.site.register(CommentaireAtelier)
admin.site.register(InscriptionAtelier)

admin.site.register(InscriptionExposant)
admin.site.register(Proposition)
admin.site.register(Message_agora)

admin.site.register(Salon)
admin.site.register(InscritSalon)
admin.site.register(InvitationDansSalon)
