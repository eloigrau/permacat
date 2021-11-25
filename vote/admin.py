from django.contrib import admin
from vote import models
# Register your models here.

admin.site.register(models.Vote)
admin.site.register(models.Suffrage)
admin.site.register(models.Question_majoritaire)
admin.site.register(models.Proposition_m)
admin.site.register(models.Question_binaire)
admin.site.register(models.ReponseQuestion_m)
admin.site.register(models.ReponseQuestion_b)
admin.site.register(models.Commentaire)