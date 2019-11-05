# -*- coding: utf-8 -*-
from .models import  Adresse, Produit, MessageGeneralPermacat, Panier, Item, Message, MessageGeneral, Conversation
from blog.models import Article, Projet, Commentaire, CommentaireProjet


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProducteurChangeForm_admin
from .models import Profil
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    form = ProducteurChangeForm_admin
    model = Profil
    list_display = ['email', 'username', 'statut_adhesion', 'date_registration', 'last_login',
                    'inscrit_newsletter']

    readonly_fields = ('date_registration','last_login','adresse')

    fieldsets = (
        (None, {'fields': ('username','description','competences','pseudo_june','statut_adhesion','adresse', 'inscrit_newsletter', 'cotisation_a_jour')}),
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

admin.site.register(Article, ArticleAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Profil, CustomUserAdmin)

admin.site.register(Adresse)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Panier)
admin.site.register(Item)
admin.site.register(Message)
admin.site.register(MessageGeneral)
admin.site.register(MessageGeneralPermacat)

admin.site.register(Conversation)
admin.site.register(Commentaire)
admin.site.register(CommentaireProjet)
