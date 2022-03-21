from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def accueil(request):
    #form = InscriptionForm(request.POST or None)
    #if form.is_valid():
    #    fiche = form.save(request.user)
    #    return redirect(fiche.get_absolute_url())
    return render(request, 'agoratransition/index.html', {})# "form": form, })
