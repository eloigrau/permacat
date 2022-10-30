from bourseLibre.views_base import DeleteAccess
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, UpdateView, DeleteView
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from bourseLibre.models import Asso
from bourseLibre.views import testIsMembreAsso
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.utils.timezone import now
from .forms import ReunionForm, ReunionChangeForm, ParticipantReunionForm, PrixMaxForm, ParticipantReunionChoiceForm
from .models import Reunion, ParticipantReunion, Choix
from bourseLibre.forms import AdresseForm, AdresseForm3
import itertools
import csv
from django.http import HttpResponse

@login_required
def lireReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    if not reunion.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso": str(reunion.asso)})

    liste_participants = [(x, x.getDistance_route(reunion), x.get_url(reunion), x.get_gmaps_url(reunion)) for x in reunion.participants.all()]

    context = {'reunion': reunion, 'liste_participants': liste_participants, }

    return render(request, 'defraiement/lireReunion.html', context,)


@login_required
def recalculerDistanceReunion(request, slug_reunion):
    reunion = get_object_or_404(Reunion, slug=slug_reunion)
    reunion.recalculerDistance()
    return redirect(reverse('defraiement:lireReunion', kwargs={"slug": slug_reunion}))


@login_required
def lireParticipant(request, id):
    part = get_object_or_404(ParticipantReunion, id=id)
    reunions = part.reunion_set.all()
    reu = [(r, part.getDistance_route(r)) for r in reunions]
    context = {"part":part, 'reunions': reu, }

    return render(request, 'defraiement/lireParticipant.html', context,)

def getRecapitulatif_km(request, reunions):
    participants = ParticipantReunion.objects.all()
    entete = ["nom", ] + ["<a href="+r.get_absolute_url()+">" +r.titre+"</a>"  + " (" + str(r.start_time) + ")" for r in reunions] + ["km parcourus",]
    lignes = []
    for p in participants:
        distances = [round(p.getDistance_route(r)*2, 2) if p in r.participants.all() else 0 for r in reunions ]
        part = ["<a href=" + p.get_absolute_url() + ">" +p.nom+"</a>", ] + distances + [round(sum(distances), 2) , ]
        lignes.append(part)
    distancesTotales = [round(r.getDistanceTotale*2, 2) for r in reunions]
    lignes.append(["Total", ] + distancesTotales + [round(sum(distancesTotales), 2), ])
    return entete, lignes

def getRecapitulatif_euros(request, reunions, prixMax, tarifKilometrique):
    participants = ParticipantReunion.objects.all()
    entete = ["nom", ] + ["<a href="+r.get_absolute_url()+">" +r.titre+"</a>" + " (" + str(r.start_time) +")" for r in reunions] + ["total Euros",]
    lignes = []

    distancesTotales = [r.getDistanceTotale for r in reunions]
    prixTotal = 2.0 * sum(distancesTotales) * float(tarifKilometrique)
    if prixTotal < float(prixMax):
        coef_distanceTotale = 2.0 * float(tarifKilometrique)
    else:
        coef_distanceTotale = float(prixMax) / prixTotal
    for p in participants:
        distances = [int(p.getDistance_route(r) * coef_distanceTotale + 0.5) if p in r.participants.all() else 0 for r in reunions ]
        part = ["<a href=" + p.get_absolute_url() + ">" +p.nom+"</a>", ] + distances + [sum(distances), ]
        lignes.append(part)
    distancesTotales = [int(r.getDistanceTotale * coef_distanceTotale + 0.5) for r in reunions]
    lignes.append(["Total", ] + distancesTotales + [sum(distancesTotales), ])
    lignes.append(["prix max : " + prixMax, "bareme kilometrique max :" + tarifKilometrique,
                   "barème calculé :" + str(round(coef_distanceTotale/2.0, 3)), ] + ["" for r in reunions[2:]] + ["", ])

    return entete, lignes

@login_required
def recapitulatif(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied

    reunions = Reunion.objects.filter(estArchive=False, asso=asso, ).order_by('start_time','categorie',)

    entete, lignes = getRecapitulatif_km(request, reunions)
    asso_list = [(x.nom, x.abreviation) for x in Asso.objects.all().exclude(abreviation="jp").order_by("id")
                            if request.user.est_autorise(x.abreviation)]
    type_list = Choix.type_reunion
    type_reunion = "tout"
    form = PrixMaxForm(request.POST or None)
    if form.is_valid():
        prixMax = form.cleaned_data["prixMax"]
        tarifKilometrique = form.cleaned_data["tarifKilometrique"]
        entete, lignes = getRecapitulatif_euros(request, reunions, prixMax, tarifKilometrique)

        return render(request, 'defraiement/recapitulatif.html', {"form": form, "entete":entete, "lignes":lignes, "unite":"euros", "asso_list":asso_list, "type_list":type_list, "asso_courante":asso.abreviation, "type_courant":type_reunion}, )

    return render(request, 'defraiement/recapitulatif.html', {"form": form, "entete":entete, "lignes":lignes, "unite":"km", "asso_list":asso_list, "type_list":type_list, "asso_courante":asso.abreviation, "type_courant":type_reunion},)

def export_recapitulatif(request, asso, type_reunion="999"):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    if type_reunion != "999":
        reunions = Reunion.objects.filter(estArchive=False, asso=asso, categorie=type_reunion).order_by('start_time','categorie',)
    else :
        reunions = Reunion.objects.filter(estArchive=False, asso=asso, ).order_by('start_time','categorie',)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="defraiement_reunions.csv"'},
    )
    writer = csv.writer(response)

    entete, lignes = getRecapitulatif_euros(request, reunions)
    writer.writerow(entete)
    for l in lignes:
        writer.writerow(l)
    entete, lignes = getRecapitulatif_km(request, reunions)
    writer.writerow(entete)
    for l in lignes:
        writer.writerow(l)
    response['Content-Disposition'] = 'attachment; filename="defraiement_reunions.csv"'
    return response


@login_required
def ajouterReunion(request):
    form = ReunionForm(request, request.POST or None)

    if form.is_valid():
        reu = form.save(request.user)
        return redirect(reverse('defraiement:ajouterAdresseReunion', kwargs={"slug": reu.slug}))

    return render(request, 'defraiement/ajouterReunion.html', { "form": form,})


@login_required
def modifierParticipantReunion(request, id):
    part = ParticipantReunion.objects.get(id=id)
    form = ParticipantReunionForm(request.POST or None, part.nom)
    form_adresse = AdresseForm(request.POST or None, instance=part.adresse)
    #form_adresse2 = AdresseForm3(request.POST or None, instance=part.adresse)

    if form.is_valid() and form_adresse.is_valid():#or form_adresse.is_valid()
        #if 'adressebtn' in request.POST:
        #    adresse = form_adresse.save()
        #else:
        adresse = form_adresse.save()
        part.nom = form.cleaned_data['nom']
        part.adresse = adresse
        part.save()
        return redirect(part.get_absolute_url())

    return render(request, 'defraiement/modifierParticipantReunion.html', {'part':part, 'form':form,'form_adresse':form_adresse})

# @login_required
class ModifierParticipant(UpdateView):
    model = ParticipantReunion
    template_name_suffix = '_modifier'
    success_url = reverse_lazy('defraiement:participants')

    def get_object(self):
        return ParticipantReunion.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

# @login_required
class ModifierReunion(UpdateView):
    model = Reunion
    form_class = ReunionChangeForm
    template_name_suffix = '_modifier'

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierReunion, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all().order_by('nom')) if self.request.user.estMembre_str(x.abreviation)]
        return form

def ajouterAdresseReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    #form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_adresse2.is_valid():#form_adresse.is_valid() or
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse2.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterAdresseReunionAdresseReunion.html', {'reunion':reunion, 'form_adresse':form_adresse, 'form_adresse2':form_adresse2 })

def modifierAdresseReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    #form_adresse = AdresseForm(request.POST or None, instance=reunion)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_adresse2.is_valid():#form_adresse.is_valid() or
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse2.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/modifierAdresseReunion.html', {'reunion':reunion, 'form_adresse2':form_adresse2 }) # 'form_adresse':form_adresse,

class SupprimerParticipant(DeleteAccess, DeleteView):
    model = ParticipantReunion
    success_url = reverse_lazy('defraiement:participants')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return ParticipantReunion.objects.get(id=self.kwargs['id'])


class SupprimerReunion(DeleteAccess, DeleteView):
    model = Reunion
    success_url = reverse_lazy('defraiement:reunions')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Reunion.objects.get(slug=self.kwargs['slug'])

@login_required
def ajouterParticipant(request):
    form = ParticipantReunionForm(request.POST or None, )
    #form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)
    if form.is_valid() and form_adresse2.is_valid(): #(form_adresse.is_valid() or
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse2.save()
        part = form.save(adresse)

        return redirect(part.get_absolute_url())

    return render(request, 'defraiement/ajouterParticipant.html', {'form': form,'form_adresse2':form_adresse2 }) # 'form_adresse':form_adresse,


@login_required
def ajouterParticipantReunion(request, slug_reunion):
    reunion = get_object_or_404(Reunion, slug=slug_reunion)
    form = ParticipantReunionForm(request.POST or None, )
    form_choice = ParticipantReunionChoiceForm(request.POST or None)
    #form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_choice.is_valid() or (form.is_valid() and form_adresse2.is_valid()):#(form_adresse.is_valid() or form_adresse2.is_valid()):
        if form_choice.is_valid():
            if form_choice.cleaned_data and form_choice.cleaned_data["participant"]:
                reunion.participants.add(form_choice.cleaned_data["participant"])
                reunion.save()
                return redirect(reunion)
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse2.save()
        participant = form.save(adresse)

        reunion.participants.add(participant)
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterParticipantReunion.html', {'reunion':reunion, 'form': form, 'form_choice':form_choice,  'form_adresse2':form_adresse2 }) ##'form_adresse':form_adresse,


@login_required
def ajouterAdresseReunion(request, slug):
    reunion = Reunion.objects.get(slug=slug)
    #form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_adresse2.is_valid(): #form_adresse.is_valid() or
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse2.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterAdresseReunion.html', {'reunion':reunion, 'form_adresse2':form_adresse2 }) #'form_adresse':form_adresse,





class SupprimerParticipantReunion(DeleteView):
    model = ParticipantReunion
    success_url = reverse_lazy('defraiement:reunions')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Reunion.objects.get(slug=self.kwargs['slug_reunion']).participants.get(id=self.kwargs['id_participantReunion'])

    def delete(self, request, *args, **kwargs):
        parti = self.get_object()
        Reunion.objects.get(slug=self.kwargs['slug_reunion']).participants.remove(parti)
        return redirect(self.get_success_url())


    def get_success_url(self):
        return Reunion.objects.get(slug=self.kwargs['slug_reunion']).get_absolute_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['reunion'] = Reunion.objects.get(slug=self.kwargs['slug_reunion'])
        return context

@login_required
def voirLieux(request,):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de voir les lieux")
    titre = "tous les lieux"
    lieux = Reunion.objects.filter().order_by('titre')

    return render(request, 'defraiement/carte_touslieux.html', {'titre':titre, "lieux":lieux})



class ListeReunions(ListView):
    model = Reunion
    context_object_name = "reunion_list"
    template_name = "reunions/reunion_list.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())
        qs = Reunion.objects.filter(estArchive=False)

        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-start_time', 'categorie', 'titre', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['list_archive'] = Reunion.objects.filter(estArchive=True)

        cat= Reunion.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_reunion if x[0] in cat]
        context['ordreTriPossibles'] = ['-date_creation', 'categorie', 'titre' ]

        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['categorie_courante'] = [x[1] for x in Choix.type_reunion if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"
        return context


class ListeReunions_asso(ListeReunions):
    def get_queryset(self):
        params = dict(self.request.GET.items())
        self.asso = Asso.objects.get(abreviation=self.kwargs['asso_slug'])
        qs = Reunion.objects.filter(estArchive=False, asso=self.asso)

        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-start_time', 'categorie', 'titre', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_courante'] = self.asso.nom
        context['asso_courante_slug'] = self.asso.abreviation
        return context

class ListeParticipants(ListView):
    model = ParticipantReunion
    context_object_name = "participant_list"
    template_name = "reunions/participant_list.html"
    paginate_by = 30

    def get_queryset(self):
        qs = ParticipantReunion.objects.all().order_by("nom")
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['list_archive'] = Reunion.objects.filter(estArchive=True)
        return context


@login_required
def lireReunion_id(request, id):
    atelier = get_object_or_404(Reunion, id=id)
    return lireReunion(request, atelier)
