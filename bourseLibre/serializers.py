from .models import Produit
from rest_framework import serializers



class ProduitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Produit
        fields = ['date_creation', 'nom_produit',  'description', 'estUneOffre']