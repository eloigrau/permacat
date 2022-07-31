# -*- coding: utf-8 -*-
from .models import Message_permagora


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

#from .forms import ProfilCreationForm, ProfilChangeForm_admin
from .models import Profil, Commentaire_charte, PropositionCharte, PoleCharte, Signataire
from django.utils.translation import gettext_lazy as _


# class CustomUserAdmin(UserAdmin):
#     add_form = ProfilCreationForm
#     form = ProfilChangeForm_admin
#     model = Profil
#     list_display = ['email', 'username', 'date_registration', 'last_login',
#                     'inscrit_newsletter']
#
#     readonly_fields = ('date_registration','last_login','adresse')
#
#     fieldsets = (
#         (None, {'fields': ('username','description','adresse', 'inscrit_newsletter', 'a_signe')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#         )

admin.site.register(Message_permagora)
admin.site.register(PoleCharte)
admin.site.register(PropositionCharte)
admin.site.register(Commentaire_charte)
admin.site.register(Signataire)