from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InscriptionForm, ContactForm, PropositionForm

# Create your views here.
def accueil(request):
    form_contact = ContactForm(request.POST or None)
    form_proposition = PropositionForm(request.POST or None)
    form_inscription = InscriptionForm(request.POST or None)
    msg = None
    msg2 = None
    if form_contact.is_valid():
        form_contact.save()
        msg2 = "Merci ! votre message a bien été envoyé"
        form_contact = ContactForm(request.POST or None)
    if form_proposition.is_valid():
        form_proposition.save()
        msg = "Merci ! votre proposition a bien été envoyée"
        form_proposition = PropositionForm(request.POST or None)
    if form_inscription.is_valid():
        form_inscription.save()
        msg = "Merci ! votre inscription a bien été envoyé"
        form_inscription = InscriptionForm(request.POST or None)
    return render(request, 'agoratransition/index.html', {"msg":msg, "msg2":msg2, "form_contact": form_contact, "form_proposition": form_proposition, "form_inscription": form_inscription, })
