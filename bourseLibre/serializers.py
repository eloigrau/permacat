from .models import Produit
from rest_framework import serializers
from agoratransition.models import InscriptionExposant



class ProduitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Produit
        fields = ['nom_produit', 'estUneOffre', 'categorie', 'date_creation', 'absolute_url']

class InscriptionAgoraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InscriptionExposant
        fields = ['nom', 'email', 'type_inscription', 'date_inscription', 'commentaire']

