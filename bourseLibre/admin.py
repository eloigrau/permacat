from django.contrib import admin
from .models import Profil, Adresse, Produit, Produit_vegetal, Produit_objet, Produit_service, Produit_aliment, Panier, Item, Message, Conversation
from blog.models import Article

admin.site.register(Profil)
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
