# -*- coding: utf-8 -*-
from .models import  Adresse, Produit, MessageGeneralPermacat, Panier, Item, Adhesion_permacat, Message, MessageGeneral, Conversation, InscriptionNewsletter
from blog.models import Article, Projet, Commentaire, CommentaireProjet, Evenement
from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
from fiches.models import Fiche, Atelier as atelier_fiche, CommentaireFiche
from ateliers.models import Atelier, CommentaireAtelier, InscriptionAtelier


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProducteurChangeForm_admin
from .models import Profil
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    form = ProducteurChangeForm_admin
    model = Profil
    list_display = ['email', 'username',  'date_notifications', 'last_login','statut_adhesion', 'statut_adhesion_rtg',
                    'inscrit_newsletter', 'date_registration']

    readonly_fields = ('date_registration','last_login','adresse')

    fieldsets = (
        (None, {'fields': ('username','description','competences','pseudo_june','statut_adhesion','statut_adhesion_rtg','adresse', 'inscrit_newsletter', 'cotisation_a_jour', 'is_jardinpartage', 'date_notifications')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

class MyModelAdmin(admin.ModelAdmin):
    list_display = ['tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'estPublic', 'estArchive')
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'estPublic', 'estArchive')
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'categorie', 'estUneOffre', 'estPublique', 'unite_prix')
class Adhesion_permacatAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_cotisation', 'montant')

admin.site.register(Article, ArticleAdmin)
admin.site.register(Art_jardin, ArticleAdmin)
admin.site.register(Evenement)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Profil, CustomUserAdmin)

admin.site.register(Adresse)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Panier)
admin.site.register(Item)
admin.site.register(Message)
admin.site.register(MessageGeneral)
admin.site.register(MessageGeneralPermacat)
admin.site.register(InscriptionNewsletter)
admin.site.register(Adhesion_permacat, Adhesion_permacatAdmin)

admin.site.register(Conversation)
admin.site.register(Commentaire)
admin.site.register(Comm_jardin)
admin.site.register(CommentaireProjet)

admin.site.register(Fiche)
admin.site.register(CommentaireFiche)
admin.site.register(atelier_fiche)


admin.site.register(Atelier)
admin.site.register(CommentaireAtelier)
admin.site.register(InscriptionAtelier)
