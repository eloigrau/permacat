from django.contrib import admin
from .models import Vote, Suffrage, Commentaire
# Register your models here.

admin.site.register(Vote)
admin.site.register(Suffrage)
admin.site.register(Commentaire)