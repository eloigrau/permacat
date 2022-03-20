from django.shortcuts import render, redirect
from django.db.models import CharField
from django.db.models.functions import Lower
from django.views.decorators.debug import sensitive_variables
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import mail_admins, send_mail, BadHeaderError
from .forms import ProfilCreationForm, ContactForm, ProfilChangeForm, MessageForm, InscriptionBenevoleForm, InscriptionExposantForm, ContactAnonymeForm, InscriptionNewsletterForm, MessageChangeForm
from .models import Profil_agora, Message, InscriptionNewsletter, InscriptionBenevole, InscriptionExposant
from django.views.generic import UpdateView, DeleteView
CharField.register_lookup(Lower, "lower")
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.db.models import Q
from django.utils.timezone import now

def handler404(request, template_name="404.html"):  #page not found
    response = render(request, "404.html")
    response.status_code = 404
    return response

def handler500(request, template_name="500.html"):   #erreur du serveur
    response = render(request, "500.html")
    response.status_code = 500
    return response

def handler403(request, template_name="403.html"):   #non autorisé
    response = render(request, "403.html")
    response.status_code = 403
    return response

def handler400(request, template_name="400.html"):   #requete invalide
    response = render(request, "400.html")
    response.status_code = 400
    return response

def bienvenue(request):
    return render(request, 'index.html',)

def presentation_site(request):
    return render(request, 'presentation_site.html')

def merci(request):
    return render(request, 'merci.html')

def faq(request):
    return render(request, 'faq.html')

def cgu(request):
    return render(request, 'cgu.html')

def fairedon(request):
    return render(request, 'fairedon.html', )


@sensitive_variables('user', 'password1', 'password2')
def register(request):
    if request.user.is_authenticated:
        return render(request, "erreur.html", {"msg": "Vous êtes déjà inscrit et connecté !"})

    form_profil = ProfilCreationForm(request.POST or None)
    if form_profil.is_valid():
        profil_courant = form_profil.save(commit=False, is_active=True)
        profil_courant.save()
        return render(request, 'userenattente.html')

    return render(request, 'registration/register.html', { "form_profil": form_profil, })


@login_required
class profil_modifier_user(UpdateView):
    model = Profil_agora
    form_class = ProfilChangeForm
    template_name_suffix = '_modifier'
    fields = ['username', 'first_name', 'last_name', 'email','description', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)



class profil_modifier(UpdateView):
    model = Profil_agora
    form_class = ProfilChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)



class profil_supprimer(DeleteView):
    model = Profil_agora
    success_url = reverse_lazy('bienvenue')

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)


@sensitive_variables('password')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_changer_form.html', {
        'form': form
    })


def contact(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ContactForm(request.POST or None, )
        else:
            form = ContactAnonymeForm(request.POST or None, )
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            message_txt = request.user.username + "(" + request.user.email + ") a envoyé le message suivant : "+ form.cleaned_data[
                'msg']
            message_html = "<p>" + request.user.username + "(" + request.user.email + "): </p><p>" + form.cleaned_data[
                'msg'] + "</p>"

            if request.user.is_authenticated:
                email = request.user.email
                nom = request.user.username
            else:
                email = form.cleaned_data['email']
                nom = form.cleaned_data['nom']

            try:
                mail_admins(sujet, message_txt, html_message=message_html)
                if form.cleaned_data['renvoi']:
                    send_mail(sujet, message_txt, email, [email, ], fail_silently=False, html_message=message_html)


                return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                       'envoyeur': nom + " (" + email + ")",
                                                       "destinataire": "administrateurs "})
            except BadHeaderError:
                return render(request, 'erreur.html', {'msg':'Invalid header found.'})

            return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})
    else:
        if request.user.is_authenticated:
            form = ContactForm(request.POST or None, )
        else:
            form = ContactAnonymeForm(request.POST or None, )
    return render(request, 'contact.html', {'form': form})





def contact_admins(request):
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            message_txt = request.user.username + "("+ request.user.email+") : " + form.cleaned_data['msg']
            message_html = "<p>"+request.user.username + "("+ request.user.email+"): </p><p>" + form.cleaned_data['msg']+"</p>"
            try:
                mail_admins(sujet, message_txt, html_message=message_html)
                if form.cleaned_data['renvoi']:
                    send_mail(sujet, message_txt, request.user.email, request.user.email, fail_silently=False, html_message=message_html)

                return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                       'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                       "destinataire": "administrateurs "})
            except BadHeaderError:
                return render(request, 'erreur.html', {'msg':'Invalid header found.'})

            return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, "isContactProducteur":False})

from django.core.mail import get_connection, EmailMultiAlternatives

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

def contact_benevoles(request):
    benevoles = list(set(InscriptionBenevole.objects.all().values_list('user__email', flat=True)))
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            message_txt = request.user.username + "("+ request.user.email+") : " + form.cleaned_data['msg']
            message_html = "<p>"+request.user.username + "("+ request.user.email+"): </p><p>" + form.cleaned_data['msg']+"</p>"
            try:
                send_mass_html_mail([(sujet, message_txt, message_html, request.user.email, benevoles),],)


                if form.cleaned_data['renvoi']:
                    send_mail(sujet, message_txt, request.user.email, request.user.email, fail_silently=False, html_message=message_html)

                return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                       'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                       "destinataire": "bénévoles "})
            except BadHeaderError:
                return render(request, 'erreur.html', {'msg':'Invalid header found.'})

            return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, "isContactProducteur":False, "msg":"Contacter les bénévoles (" + ", ".join(benevoles)+")"})


def contact_exposants(request):
    benevoles = list(set(InscriptionExposant.objects.all().values_list('user__email', flat=True)))
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            message_txt = request.user.username + "("+ request.user.email+") : " + form.cleaned_data['msg']
            message_html = "<p>"+request.user.username + "("+ request.user.email+"): </p><p>" + form.cleaned_data['msg']+"</p>"
            try:
                send_mass_html_mail([(sujet, message_txt, message_html, request.user.email, benevoles),],)


                if form.cleaned_data['renvoi']:
                    send_mail(sujet, message_txt, request.user.email, request.user.email, fail_silently=False, html_message=message_html)

                return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                       'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                       "destinataire": "Exposants "})
            except BadHeaderError:
                return render(request, 'erreur.html', {'msg':'Invalid header found.'})

            return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form, "isContactProducteur":False, "msg":"Contacter les exposants (" + ", ".join(benevoles)+")"})


def liens(request):
    liens = [
        'https://www.facebook.com/ramenetagraine/',
        'https://www.facebook.com/permamap66/',
        'https://www.facebook.com/permapat/',
        'https://www.permapat.com/',
        'http://www.perma.cat',
        'https://framacarte.org/m/3427/ ',
        'https://alternatiba.eu/alternatiba66/',
    ]

    return render(request, 'liens.html', {'liens':liens, })


@login_required
def forum(request, ):
    messages = Message.objects.all().order_by("date_creation")
    form = MessageForm(request.POST or None)
    if form.is_valid():
        message = form.save(commit=False)
        message.auteur = request.user
        message.save()
        return redirect(request.path)
    return render(request, 'forum.html', {'form': form, 'messages_echanges': messages})


class ModifierMessage(UpdateView):
    model = Message
    form_class = MessageChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return Message.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.message and self.object.message !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return redirect("forum")




@login_required
def profil_courant(request, ):
    inscriptions_benevole = InscriptionBenevole.objects.filter(user=request.user)
    inscriptions_exposants = InscriptionExposant.objects.filter(user=request.user)
    return render(request, 'registration/profil.html', {'user': request.user, 'inscriptions_benevole':inscriptions_benevole, 'inscriptions_exposants':inscriptions_exposants})


@login_required
def profil(request, user_id):
    try:
        user = Profil_agora.objects.get(id=user_id)
        inscriptions_benevole = InscriptionBenevole.objects.filter(user=user)
        inscriptions_exposants = InscriptionExposant.objects.filter(user=user)
        return render(request, 'registration/profil.html', {'user': user, 'inscriptions_benevole':inscriptions_benevole, 'inscriptions_exposants':inscriptions_exposants})
    except User.DoesNotExist:
            return render(request, 'registration/profil_inconnu.html', {'userid': user_id})

@login_required
def profil_nom(request, user_username):
    try:
        user = Profil_agora.objects.get(username=user_username)
        inscriptions_benevole = InscriptionBenevole.objects.filter(user=user)
        inscriptions_exposants = InscriptionExposant.objects.filter(user=user)
        return render(request, 'registration/profil.html', {'user': user, 'inscriptions_benevole':inscriptions_benevole, 'inscriptions_exposants':inscriptions_exposants})
    except User.DoesNotExist:
        return render(request, 'registration/profil_inconnu.html', {'userid': user_username})


def benevoles(request):
    return render(request, 'agoratransition/benevoles.html', )


@login_required
def inscription_benevole(request):
    form = InscriptionBenevoleForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.user = request.user
        inscription.save()
        return render(request, 'merci.html', {'msg' :"Votre inscription en tant que bénévole a bien été enregistrée.", "msg2":" Vous serez contacté dès que possible. "})

    return render(request, 'agoratransition/inscription_benevole.html', {'form':form})


def exposants(request):
    return render(request, 'agoratransition/exposants.html', )


@login_required
def inscription_exposant(request):
    form = InscriptionExposantForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.user = request.user
        inscription.save()
        return render(request, 'merci.html', {'msg' :"L'inscription de votre stand a bien été enregistrée", "msg2":"p>Vous pouvez le compléter ou le modifier à tout moment sur votre profil. Vous serez contacté dès que possible.</p><p> Pour valider votre inscription, vous devez maintenant envoyer <b>un chèque de caution de 50 euros (qui ne sera pas encaissé sauf désistement) adressé à Ramene Ta Graine à l'adresse suivante : </p><p class='textcenter'>'7 rue Saint Roch, 66200 Elne'</b>. </p><p>Si vous n'êtes pas adhérent, il faut aussi adhérer à l'association en envoyant un deuxème chèque de 5 euros à la même adresse.</p><p> Merci !</p>"
                                                                                                                   ""})
    return render(request, 'agoratransition/inscription_exposant.html', {'form':form})



@login_required
def inscription_benevole_modifier(request, id):
    inscription = get_object_or_404(InscriptionBenevole, id=id)

    form = InscriptionBenevoleForm(request.POST or None, instance=inscription)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profil_courant')
    return render(request, 'agoratransition/inscription_benevole.html', {'form':form})

@login_required
def inscription_benevole_annuler(request, id):
    inscription = get_object_or_404(InscriptionBenevole, id=id)
    inscription.statut_benevole = '4'
    inscription.save()
    return redirect('profil_courant')

@login_required
def inscription_benevole_desannuler(request, id):
    inscription = get_object_or_404(InscriptionBenevole, id=id)
    inscription.statut_benevole = '0'
    inscription.save()
    return redirect('profil_courant')

@login_required
def inscription_exposant_modifier(request, id):
    inscription = get_object_or_404(InscriptionExposant, id=id)

    form = InscriptionExposantForm(request.POST or None, instance=inscription)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profil_courant')
    return render(request, 'agoratransition/inscription_exposant.html', {'form':form})


@login_required
def inscription_exposant_annuler(request, id):
    inscription = get_object_or_404(InscriptionExposant, id=id)
    inscription.statut_exposant = '4'
    inscription.save()
    return redirect('profil_courant')

@login_required
def inscription_exposant_desannuler(request, id):
    inscription = get_object_or_404(InscriptionExposant, id=id)
    inscription.statut_exposant = '0'
    inscription.save()
    return redirect('profil_courant')

def organisation(request, ):
    return render(request, 'agoratransition/organisation.html')



def inscription_newsletter(request):
    form = InscriptionNewsletterForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.save()
        return render(request, 'merci.html', {'msg' :"Vous êtes inscrits à la newsletter"})
    return render(request, 'inscription_newsletter.html', {'form':form})


@login_required
def voir_inscrits(request):
    if not request.user.is_equipe:
        return render(request, 'erreur.html', {'msg' :"Désolé vous n'êtes pas enregistré comme membre equipe de Ramene Ta Graine, contactez les administrateurs..."})
    newsletter = InscriptionNewsletter.objects.all()
    news_inscrits = Profil.objects.filter(inscrit_newsletter=True)
    inscription_exposant = InscriptionExposant.objects.all()
    inscription_benevole = InscriptionBenevole.objects.filter(~Q(statut_benevole = "4"))


    return render(request, 'agoratransition/voir_inscrits.html', {'newsletter':newsletter, 'news_inscrits':news_inscrits, 'benevoles':inscription_benevole, 'exposants':inscription_exposant})
