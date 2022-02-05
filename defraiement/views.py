from bourseLibre.views_base import DeleteAccess
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, UpdateView, DeleteView
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from bourseLibre.models import Asso

from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.utils.timezone import now
from .forms import ReunionForm, ReunionChangeForm, ParticipantReunionForm, AdresseReunionForm, ParticipantReunionChoiceForm
from .models import Reunion, ParticipantReunion, Choix
from bourseLibre.forms import AdresseForm, AdresseForm3

@login_required
def ajouterReunion(request):
    form = ReunionForm(request, request.POST or None)
    form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form.is_valid() and (form_adresse.is_valid() or form_adresse2.is_valid()):
        if 'adressebtn' in request.POST:
            adresse = form_adresse.save()
        else:
            adresse = form_adresse2.save()
        reu = form.save(request.user, adresse)
        return redirect(reu)

    return render(request, 'defraiement/ajouterReunion.html', { "form": form, })


# @login_required
class ModifierReunion(UpdateView):
    model = Reunion
    form_class = ReunionChangeForm
    template_name_suffix = '_modifier'

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save(sendMail=form.changed_data!=['estArchive'])

        #envoi_emails_reunionouprojet_modifie(self.object, "L'reunion " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierReunion, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all().order_by('nom')) if self.request.user.estMembre_str(x.abreviation)]
        return form

def modifierAdresseReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_adresse.is_valid() or form_adresse2.is_valid():
        if 'adressebtn' in request.POST:
            adresse = form_adresse.save()
        else:
            adresse = form_adresse2.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/modifierAdresseReunion.html', {'reunion':reunion, 'form_adresse':form_adresse, 'form_adresse2':form_adresse2 })


class SupprimerReunion(DeleteAccess, DeleteView):
    model = Reunion
    success_url = reverse_lazy('defraiement:reunions')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Reunion.objects.get(slug=self.kwargs['slug'])

@login_required
def ajouterParticipantReunion(request, slug_reunion):
    reunion = get_object_or_404(Reunion, slug=slug_reunion)
    form = ParticipantReunionForm(request.POST or None)
    form_choice = ParticipantReunionChoiceForm(request.POST or None)
    form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_choice.is_valid() or form.is_valid() and (form_adresse.is_valid() or form_adresse2.is_valid()):
        if form_choice.is_valid():
            if form_choice.cleaned_data and form_choice.cleaned_data["participant"]:
                reunion.participants.add(form_choice.cleaned_data["participant"])
                reunion.save()
                return redirect(reunion)
        if 'adressebtn' in request.POST:
            adresse = form_adresse.save()
        else:
            adresse = form_adresse2.save()
        participant = form.save(adresse)

        reunion.participants.add(participant)
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterParticipantReunion.html', {'reunion':reunion, 'form': form, 'form_choice':form_choice, 'form_adresse':form_adresse, 'form_adresse2':form_adresse2 })


@login_required
def ajouterAdresseReunion(request, id_reunion):
    reunion = Reunion.objects.get(id=id_reunion)
    form = AdresseReunionForm(request.POST or None)
    form_adresse = AdresseForm(request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form.is_valid() and (form_adresse.is_valid() or form_adresse2.is_valid()):
        if 'adressebtn' in request.POST:
            adresse = form_adresse.save()
        else:
            adresse = form_adresse2.save()
        reu = form.save(reunion, adresse)
        return redirect(reu)

    return render(request, 'defraiement/ajouterAdresse.html', {'reunion':reunion, 'form': form, 'form_adresse':form_adresse, 'form_adresse2':form_adresse2 })


class SupprimerParticipantReunion(DeleteView):
    model = ParticipantReunion
    success_url = reverse_lazy('defraiement:reunions')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return ParticipantReunion.objects.get(id=self.kwargs['id_participant'])

    def get_success_url(self):
        return Reunion.objects.get(slug=self.kwargs['slug_reunion']).get_absolute_url()

    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.reunion.estModifiable or self.object.reunion.auteur == request.user or request.user.is_superuser:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")


@login_required
def voirLieux(request,):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de voir les lieux")
    titre = "tous les lieux"
    lieux = Reunion.objects.filter().order_by('titre')

    return render(request, 'defraiement/carte_touslieux.html', {'titre':titre, "lieux":lieux})


@login_required
def lireReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    if not reunion.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso": str(reunion.asso)})

    liste_participants = [(x, x.get_adresse_str(), x.getDistance(reunion),x.getDistance_route(reunion)) for x in reunion.participants.all()]


    context = {'reunion': reunion, 'liste_participants': liste_participants, }

    return render(request, 'defraiement/lireReunion.html', context,)



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


@login_required
def lireReunion_id(request, id):
    atelier = get_object_or_404(Reunion, id=id)
    return lireReunion(request, atelier)
