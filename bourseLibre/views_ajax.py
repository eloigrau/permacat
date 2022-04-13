from .models import Produit

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import ProduitSerializer


class AnnoncesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Produit.objects.select_subclasses().order_by('-date_creation')
    serializer_class = ProduitSerializer
    http_method_names = ['get',]
    #permission_classes = [permissions.IsAuthenticated]


def ajax_annonces(request):
    try:
        qs = Produit.objects.select_subclasses()
        cle = request.GET.get('cle')
        if not cle == "thomas":
            return render(request, 'ajax/annonces_list.html', {"qs":qs})
        return render(request, 'ajax/annonces_list.html', {})
    except:
        pass#return render(request, 'blog/ajax/categories_dropdown_list_options.html', {'categories': Choix.get_type_annonce_asso("defaut")})

