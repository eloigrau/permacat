# -*- coding: utf-8 -*-
from .models import  Adresse, Produit, Panier, Item, Adhesion_permacat, Asso, MessageGeneral, Conversation, InscriptionNewsletter
from blog.models import Article, Projet, Commentaire, CommentaireProjet, Evenement, EvenementAcceuil
from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
from fiches.models import Fiche, Atelier as atelier_fiche, CommentaireFiche
from ateliers.models import Atelier, CommentaireAtelier, InscriptionAtelier
from django.contrib.admin.models import LogEntry


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProducteurChangeForm_admin
from .models import Profil
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    form = ProducteurChangeForm_admin
    model = Profil
    list_display = ['email', 'username',  'last_login', 'date_notifications', 'adherent_pc', 'adherent_rtg','adherent_fer','adherent_gt',
                    'inscrit_newsletter', ]

    readonly_fields = ('date_registration','last_login','adresse')

    fieldsets = (
        (None, {'fields': ('username','description','competences','pseudo_june','statut_adhesion', 'adherent_pc', 'adherent_rtg','adherent_fer',  'adherent_gt', 'adresse', 'inscrit_newsletter', 'is_jardinpartage', 'date_notifications')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )


class ArticleAdmin(admin.ModelAdmin):
        list_display = ('titre', 'asso', 'categorie', 'estArchive', )
class Article_jardinAdmin(admin.ModelAdmin):
        list_display = ('titre', 'jardin', 'categorie', 'estArchive', )
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'estArchive')
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'categorie', 'estUneOffre', 'asso', 'unite_prix')
class Adhesion_permacatAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_cotisation', 'montant')

admin.site.register(Article, ArticleAdmin)
admin.site.register(Art_jardin, Article_jardinAdmin)
admin.site.register(Evenement)
admin.site.register(EvenementAcceuil)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Profil, CustomUserAdmin)

admin.site.register(Adresse)
admin.site.register(Asso)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Panier)
admin.site.register(Item)
admin.site.register(MessageGeneral)
admin.site.register(InscriptionNewsletter)
admin.site.register(Adhesion_permacat, Adhesion_permacatAdmin)

admin.site.register(Conversation)
admin.site.register(Commentaire)
admin.site.register(Comm_jardin)
admin.site.register(CommentaireProjet)

admin.site.register(Fiche)
admin.site.register(CommentaireFiche)
admin.site.register(atelier_fiche)

admin.site.register(LogEntry)

admin.site.register(Atelier)
admin.site.register(CommentaireAtelier)
admin.site.register(InscriptionAtelier)

