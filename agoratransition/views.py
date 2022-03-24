from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InscriptionForm, ContactForm, PropositionForm

# Create your views here.
def accueil(request):
    form_contact = ContactForm(request.POST or None)
    form_proposition = PropositionForm(request.POST or None)
    form_inscription = InscriptionForm(request.POST or None)
    if form_contact.is_valid():
        form_contact.save()
        form_contact = ContactForm(request.POST or None)
    if form_proposition.is_valid():
        form_proposition.save()
        form_proposition = PropositionForm(request.POST or None)
    if form_inscription.is_valid():
        form_inscription.save()
        form_inscription = InscriptionForm(request.POST or None)
    return render(request, 'agoratransition/index.html', {"form_contact": form_contact, "form_proposition": form_proposition, "form_inscription": form_inscription, })
