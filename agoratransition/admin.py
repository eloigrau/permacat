# -*- coding: utf-8 -*-
from .models import  Message, InscriptionExposant, InscriptionBenevole, InscriptionNewsletter


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfilCreationForm, ProfilChangeForm_admin
from .models import Profil_agora
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    add_form = ProfilCreationForm
    form = ProfilChangeForm_admin
    model = Profil_agora
    list_display = ['email', 'username', 'date_registration', 'last_login',
                    'inscrit_newsletter',]

    readonly_fields = ('date_registration','last_login','code_postal')

    fieldsets = (
        (None, {'fields': ('username','description','commune', 'code_postal', 'is_equipe', 'inscrit_newsletter')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

admin.site.register(Profil_agora, CustomUserAdmin)
admin.site.register(Message)
admin.site.register(InscriptionBenevole)
admin.site.register(InscriptionExposant)
admin.site.register(InscriptionNewsletter)