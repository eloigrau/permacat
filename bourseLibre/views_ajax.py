from .models import Produit

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import ProduitSerializer


class AnnoncesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = ProduitSerializer
    http_method_names = ['get',]
    #permission_classes = [permissions.IsAuthenticated]
    queryset = Produit.objects.select_subclasses().order_by('-date_creation')

    def get_queryset(self):
        cle = self.request.query_params.get('cle')
        queryset = Produit.objects.filter(nom_produit="aaaaa")
        if cle == "thomas":
            queryset = Produit.objects.select_subclasses().order_by('-date_creation')

        return queryset


def ajax_annonces(request):
    try:
        qs = Produit.objects.filter(asso="Public").select_subclasses()[:10]
        cle = request.GET.get('cle')
        if not cle == "thomas":
            return render(request, 'ajax/annonces_list.html', {})
        return render(request, 'ajax/annonces_list.html', {"qs":qs})
    except:
        pass#return render(request, 'blog/ajax/categories_dropdown_list_options.html', {'categories': Choix.get_type_annonce_asso("defaut")})

