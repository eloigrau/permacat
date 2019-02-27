import datetime
from haystack import indexes
from .models import Profil,  Produit #_objet, Produit_service, Produit_vegetal, Produit_aliment
from blog.models import Article

class ProduitIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='description', use_template=True)
    nom_produit = indexes.CharField(model_attr='nom_produit')
    date_debut = indexes.CharField(model_attr='date_debut')

    def get_model(self):
        return Produit

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

# class Produit_alimentIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, model_attr='description', use_template=True)
#     nom_produit = indexes.CharField(model_attr='nom_produit')
#     date_debut = indexes.CharField(model_attr='date_debut')
#
#     def get_model(self):
#         return Produit_aliment
#
#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()
#
# class Produit_vegetalIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, model_attr='description', use_template=True)
#     nom_produit = indexes.CharField(model_attr='nom_produit')
#     date_debut = indexes.CharField(model_attr='date_debut')
#
#     def get_model(self):
#         return Produit_vegetal
#
#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()
# class Produit_serviceIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, model_attr='description', use_template=True)
#     nom_produit = indexes.CharField(model_attr='nom_produit')
#     date_debut = indexes.CharField(model_attr='date_debut')
#
#     def get_model(self):
#         return Produit_service
#
#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()
# class Produit_objetIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, model_attr='description', use_template=True)
#     nom_produit = indexes.CharField(model_attr='nom_produit')
#     date_debut = indexes.CharField(model_attr='date_debut')
#
#     def get_model(self):
#         return Produit_objet
#
#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()

class ProfilIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    date_registration = indexes.DateTimeField(model_attr='date_registration')

    def get_model(self):
        return Profil

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()#filter(pub_date__lte=datetime.datetime.now())

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='titre', document=True,)
    auteur = indexes.CharField(model_attr='user')
    categorie = indexes.CharField(model_attr='categorie')
    auteur = indexes.CharField(model_attr='auteur')
    date= indexes.DateTimeField(model_attr='date')
    contenu = indexes.CharField(model_attr='contenu')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()#filter(pub_date__lte=datetime.datetime.now())
