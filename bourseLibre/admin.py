from django.contrib import admin
from .models import Profil, Adresse, Produit, Produit_vegetal, Produit_objet, Produit_service, Produit_aliment, Panier, Item, Message, Conversation
from blog.models import Article
# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import User

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProducteurChangeForm
from .models import Profil

class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    #form = ProducteurChangeForm
    model = Profil
    #list_display = ['email', 'username',]

admin.site.register(Profil, CustomUserAdmin)

# class MyUserCreationForm(UserCreationForm):
#     def clean_username(self):
#         username = self.cleaned_data["username"]
#         try:
#             User._default_manager.get(username=username)
#         except User.DoesNotExist:
#             return username
#         raise forms.ValidationError(self.error_messages['duplicate_username'])
#
#     class Meta(UserCreationForm.Meta):
#         model = User
#
#
# class UserAdmin(AuthUserAdmin):
#     add_form = MyUserCreationForm
#     update_form_class = UserChangeForm
#
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

admin.site.register(Adresse)
admin.site.register(Produit)
admin.site.register(Produit_vegetal)
admin.site.register(Produit_objet)
admin.site.register(Produit_service)
admin.site.register(Produit_aliment)
admin.site.register(Panier)
admin.site.register(Item)
admin.site.register(Message)

admin.site.register(Conversation)
admin.site.register(Article)
