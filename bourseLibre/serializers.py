from .models import Produit
from rest_framework import serializers



class ProduitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Produit
        fields = ['nom_produit', 'estUneOffre', 'categorie', 'date_creation', 'absolute_url']