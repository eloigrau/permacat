from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InscriptionForm, ContactForm, PropositionForm

# Create your views here.
@login_required
def accueil(request):
    form_contact = ContactForm(request.POST or None)
    form_proposition = PropositionForm(request.POST or None)
    form_inscription = InscriptionForm(request.POST or None)
    if form_contact.is_valid():
        ins = form_contact.save()
        return redirect(request.path)
    if form_proposition.is_valid():
        ins = form_proposition.save()
        return redirect(request.path)
    if form_inscription.is_valid():
        ins = form_inscription.save()
        return redirect(request.path)
    return render(request, 'agoratransition/index.html', {"form_contact": form_contact, "form_proposition": form_proposition, "form_inscription": form_inscription, })
