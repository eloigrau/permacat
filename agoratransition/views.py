from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InscriptionForm, ContactForm, PropositionForm
from .models import InscriptionExposant
from bourseLibre.serializers import InscriptionAgoraSerializer
from rest_framework import viewsets
from rest_framework import permissions

# Create your views here.
def accueil(request):
    form_contact = ContactForm(request.POST or None)
    form_proposition = PropositionForm(request.POST or None)
    form_inscription = InscriptionForm(request.POST or None)
    msg = None
    msg2 = None
    anchor = None

    if request.method == 'POST' and 'inscriptionbtn' in request.POST:
        anchor = "inscription"
        if form_inscription.is_valid() :
            form_inscription.save()
            msg = "Votre inscription a bien été envoyée, merci ! Vous allez recevoir un mail de confimation."
        elif form_inscription.errors:
            if [x for x in form_inscription.errors.items()][0][1][0]  == "Un object Inscription exposant avec ces champs Nom Prénom / Raison sociale* et Email* existe déjà.":
                msg = "Vous êtes bien enregistré"
            else:
                msg = "Une erreur s'est produite lors de votre inscription, veuillez réessayer ou  nous contacter"


    if request.method == 'POST' and 'contactbtn' in request.POST:
        anchor = "contact"
        if form_contact.is_valid():
            form_contact.save()
            msg2 = "Votre message a bien été envoyé, merci !"
        elif form_contact.errors:
            msg2 = "Une erreur s'est produite lors de l'envoi du message, veuillez réessayer"

    if request.method == 'POST' and 'proposbtn' in request.POST:
        anchor = "inscription"
        if form_proposition.is_valid():
            form_proposition.save()
            msg = "Votre proposition a bien été envoyée, merci !"
        elif form_proposition.errors:
            msg = "Une erreur s'est produite lors de l'envoi de la proposition"

    return render(request, 'agoratransition/index.html', {"msg":msg, "msg2":msg2, "form_contact": form_contact, "form_proposition": form_proposition, "form_inscription": form_inscription, "anchor":anchor })

@login_required
def listeInscription(request, ):
    listeMails = []
    if request.user.is_superuser:
      listeMails.append({"type":'inscrits', "profils":InscriptionExposant.objects.all(), "titre":"Liste des inscrits : "})

    return render(request, 'listeContacts.html', {"listeMails":listeMails, "asso":"" })


class InscriptionsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = InscriptionAgoraSerializer
    http_method_names = ['get',]
    permission_classes = [permissions.IsAuthenticated]
    queryset = InscriptionExposant.objects.all().order_by('nom')
