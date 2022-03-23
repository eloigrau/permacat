from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import InscriptionExposantForm

# Create your views here.
@login_required
def accueil(request):
    form = InscriptionExposantForm(request.POST or None)
    if form.is_valid():
        ins = form.save()
    return render(request, 'agoratransition/index.html', {"form": form, })
