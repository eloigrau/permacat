# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from actstream.models import Action, Follow
from .models import Profil, Conversation, Suivis, Adresse
from .settings import LOCALL
from .settings.production import SERVER_EMAIL, EMAIL_HOST_PASSWORD
from django.http import HttpResponseForbidden
from django.core.mail.message import EmailMultiAlternatives
import re
from django.core import mail
from actstream import actions
from bs4 import BeautifulSoup
from .forms import Adhesion_permacatForm, Adhesion_assoForm, creerAction_articlenouveauForm
from actstream import action
from actstream.models import followers

def getMessage(action):
    message = action.data['message']
    if "a commenté" in message:
        mess = message.split("a commenté ")
        message = mess[1] + " a été commenté"
    return message


def getListeMailsAlerte():
    actions = Action.objects.filter(verb='emails')
    print('Nb actions : ' + str(len(actions)))
    messagesParMails = {}
    for action in actions:
        if 'emails' in action.data:
            for mail in action.data['emails']:
                message = getMessage(action)
                if not mail in messagesParMails:
                    messagesParMails[mail] = [message, ]
                else:
                    for x in messagesParMails[mail]:
                        if not message in messagesParMails[mail]:
                            messagesParMails[mail].append(message)

    listeMails = []
    for mail, messages in messagesParMails.items():
        titre = "[Perma.Cat] Du nouveau sur Perma.Cat"
        try:
            pseudo = Profil.objects.get(email=mail).username
        except:
            pseudo = ""
        messagetxt = "Bonjour / Bon dia, Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :\n"
        message = "<p>Bonjour / Bon dia,</p><p>Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :</p><ul>"
        liste_messages = []
        for m in messages:
            liste_messages.append("<li>" + m + "</li>")
            try:
                r = re.search("htt(.*?)>", m).group(1)[:-1]
                messagetxt += re.sub('<[^>]+>', '', m) + " : htt" + r + "\n"
            except:
                messagetxt += re.sub('<[^>]+>', '', m) + "\n"
        liste_messages.sort()
        message += "".join(liste_messages)

        messagetxt += "\nFins Aviat !\n---------------\nPour voir toute l'activité sur le site, consultez les Notifications : https://www.perma.cat/notifications/activite/ \n" + \
                      "Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou consultez la FAQ : https://www.perma.cat/faq/) "
        message += "</ul><br><p>Fins Aviat !</p><hr>" + \
                   "<p><small>Pour voir toute l'activité sur le site, consultez les <a href='https://www.perma.cat/notifications/activite/'>Notifications </a> </small>. " + \
                   "<small>Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou supprimez  <a href='https://www.perma.cat/accounts/mesSuivis/'>vos abonnements</a> ou consultez la <a href='https://www.perma.cat/faq/'>FAQ</a>)</small></p>"

        listeMails.append((titre, messagetxt, message, SERVER_EMAIL, [mail, ]))

    seen = set()
    listeMails_ok = []
    for x in listeMails:
        if x[1] not in seen:
            seen.add(x[1])
            listeMails_ok.append(x)
        else:
            i = next((i for i, mail in enumerate(listeMails_ok) if x[1] in mail), None)
            listeMails_ok[i][4].append(x[4][0])

    return listeMails_ok


def supprimerActionsEmails():
    actions = Action.objects.filter(verb='emails')
    for action in actions:
        action.delete()


def supprimerActionsStartedFollowing():
    actions = Action.objects.filter(verb='started following')
    for action in actions:
        action.delete()


def nettoyerActions(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    actions = Action.objects.all()
    for action in actions:
        try:
            print(action)
        except:
            action.delete()
    return redirect("bienvenue")


def abonnerAdherentsCiteAlt(request, ):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    profils = Profil.objects.filter(adherent_citealt=True)
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_citealt')

    for prof in profils:
        actions.follow(prof, suivi, actor_only=True, send_action=False)

    return redirect("bienvenue")


def nettoyerFollows(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    follows = Follow.objects.filter(user=request.user)
    for action in follows:
        if not action.follow_object:
            action.delete()

        if isinstance(action.follow_object, Conversation):
            # print("follow supprimé " + action)
            action.delete()

    actions = Action.objects.all()

    return render(request, 'admin/voirActions.html', {'actions': actions, })


def nettoyerHistoriqueAdmin(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    from django.contrib.admin.models import LogEntry
    actions = LogEntry.objects.all()
    for action in actions:
        action.delete()

    return render(request, 'admin/voirActions.html', {'actions': actions, })


def get_articles_a_archiver():
    from blog.models import Article, Evenement
    from datetime import datetime, timedelta, date
    import pytz
    utc = pytz.UTC
    date_limite = utc.localize(datetime.today() - timedelta(days=90))
    articles = Article.objects.filter(estArchive=False, start_time__lte=date_limite, end_time__lte=date_limite)

    liste = []
    for article in articles:
        if article.start_time:
            liste.append(article)
    liste2 = []
    from jardinpartage.models import Article as Article_jardin, Evenement as Evenement_jardin
    articles = Article_jardin.objects.filter(estArchive=False, start_time__lte=date_limite, end_time__lte=date_limite)
    for article in articles:
        if article.start_time:
            liste2.append(article)
    liste3 = []
    for art in liste:
        eve = Evenement.objects.filter(start_time__lt=date_limite, end_time__lte=date_limite, article=art)
        if eve:
            liste3.append(art)

    for art in liste2:
        eve = Evenement_jardin.objects.filter(start_time__lt=date_limite, end_time__lte=date_limite, article=art)
        if eve:
            liste3.append(art)

    return liste, liste2, liste3


def voir_articles_a_archiver(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    liste, liste2, liste3 = get_articles_a_archiver()
    return render(request, 'admin/voirArchivage.html', {'liste': liste, 'liste2': liste2, 'liste3': liste3})


def archiverArticles(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    liste, liste2, liste3 = get_articles_a_archiver()
    for art in liste:
        art.estArchive = True
        art.save()
    for art in liste2:
        art.estArchive = True
        art.save()
    return redirect('voir_articles_a_archiver', )


def voirEmails(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    listeMails = getListeMailsAlerte()
    return render(request, 'admin/voirEmails.html', {'listeMails': listeMails, })


def send_mass_html_mail(datatuple, fail_silently=False, auth_user=None,
                        auth_password=None, connection=None):
    """
    Given a datatuple of (subject, message, html_message, from_email,
    recipient_list), send each message to each recipient list.
    Return the number of emails sent.
    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user and auth_password are set, use them to log in.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.
    """
    #import re
    #EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    data = []
    for subject, message, html_message, sender, recipient in datatuple:
        if len(recipient) > 90:
            for i in range(0, len(recipient), 90):
                data.append([subject, message, html_message, sender, recipient[i:i + 90]])
        else:
            data.append([subject, message, html_message, sender, recipient])

    connection = mail.get_connection(
        username=SERVER_EMAIL,
        password=EMAIL_HOST_PASSWORD,
        fail_silently=fail_silently,
    )
    messages = [
        EmailMultiAlternatives(subject, message, sender, to=[SERVER_EMAIL, ],
                               bcc=recipient,
                               alternatives=[(html_message, 'text/html')],
                               connection=connection)
        for subject, message, html_message, sender, recipient in data if recipient != [SERVER_EMAIL,]
    ]
    return connection.send_messages(messages)


def envoyerEmailsRequete(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    listeMails = getListeMailsAlerte()
    send_mass_html_mail(listeMails, fail_silently=False)
    supprimerActionsEmails()
    supprimerActionsStartedFollowing()
    return redirect('voirEmails', )

def envoyerEmailsTest(request):
    listeMails = []
    for i in range(2):
        listeMails.append(("titre", "messagetxt", "message_" + str(i), SERVER_EMAIL, [j for j in range(205)]))

    send_mass_html_mail(listeMails, fail_silently=False)

def envoyerEmails():
    print('Récupération des mails')
    listeMails = getListeMailsAlerte()

    print('Envoi des mails' + str(listeMails))
    send_mass_html_mail(listeMails, fail_silently=False)
    print('Suppression des alertes')
    supprimerActionsEmails()
    # supprimerActionsStartedFollowing()
    print('Fait')


def envoyerEmailstest():
    listeMails = []
    listeMails.append(('testCron', "message en txt", "<b>le message html</b>", SERVER_EMAIL, ["eloi.grau@gmail.com", ]))
    send_mass_html_mail(listeMails, fail_silently=False)


def decalerEvenements(request, num):
    return HttpResponseForbidden()
    #
    # from blog.models import Article, Projet, Evenement
    # from datetime import timedelta
    # decalage = timedelta(days=1)
    # if num == 0:
    #     for i, article in enumerate(Article.objects.all()):
    #             if article.start_time:
    #                 article.start_time = article.start_time + decalage
    #                 article.save()
    #                 print("ok1_"+str(i) + str(article))
    #             if article.end_time:
    #                 article.end_time = article.end_time + decalage
    #                 article.save()
    #                 print("ok2_"+str(i) + str(article))
    # if num == 1:
    #     for i, projet in enumerate(Projet.objects.all()):
    #             if projet.start_time:
    #                 projet.start_time = projet.start_time + decalage
    #                 projet.save()
    #                 print("ok1_"+str(i) + str(projet))
    #             if projet.end_time:
    #                 projet.end_time = projet.end_time + decalage
    #                 projet.save()
    #                 print("ok2_"+str(i) + str(projet))
    # if num == 2:
    #     for i, evenement in enumerate(Evenement.objects.all()):
    #             if evenement.start_time:
    #                 evenement.start_time = evenement.start_time + decalage
    #                 evenement.save()
    #                 print("ok1_"+str(i)+"_" + str(evenement))
    #             if evenement.end_time:
    #                 evenement.end_time = evenement.end_time + decalage
    #                 evenement.save()
    #                 print("ok2_" +str(i)+ str(evenement))
    #
    # if num == 3:
    #     from jardinpartage.models import Article as ArticleJP
    #     for i, evenement in enumerate(ArticleJP.objects.all()):
    #             if evenement.start_time:
    #                 evenement.start_time = evenement.start_time + decalage
    #                 evenement.save()
    #                 print("ok1_"+str(i)+"_" + str(evenement))
    #             if evenement.end_time:
    #                 evenement.end_time = evenement.end_time + decalage
    #                 evenement.save()
    #                 print("ok2_" +str(i)+ str(evenement))

    return redirect('bienvenue')


def voirPbProfils(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    adresses = Adresse.objects.all()
    pb_adresses = []
    for add in adresses:
        if add.getDistance(request.user.adresse) > 500:
            add.set_latlon_from_adresse()
            if add.getDistance(request.user.adresse) > 500:
                if add.code_postal == 66000:
                    add.commune = "Perpignan"
                    add.save()
                    add.set_latlon_from_adresse()
                    if add.getDistance(request.user.adresse) > 500:
                        pb_adresses.append(add)
    import requests
    profils = Profil.objects.all()
    pb_profils = []
    for profil in profils:
        if profil.description and not bool(BeautifulSoup(profil.description, "html.parser").find()):
            try:
                r = requests.post('https://validator.w3.org/nu/',
                                  data=profil.description, params={'out': 'json'},
                                  headers={
                                      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101    Safari/537.36',
                                      'Content-Type': 'text/html; charset=UTF-8'})

                pb_profils.append([profil, profil.description, r, ""])
            except:
                pb_profils.append([profil, profil.description, "none", "none"])

        if profil.competences and not bool(BeautifulSoup(profil.competences, "html.parser").find()):
            try:
                r = requests.post('https://validator.w3.org/nu/',
                                  data=profil.competences, params={'out': 'json'},
                                  headers={
                                      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101    Safari/537.36',
                                      'Content-Type': 'text/html; charset=UTF-8'})

                pb_profils.append([profil, profil.competences, r, ""])
            except:
                pb_profils.append([profil, profil.competences, "none", "none"])

    return render(request, 'admin/voirPbProfils.html', {'pb_profils': pb_profils, 'pb_adresses': pb_adresses})



def ajouterAdhesion(request, abreviationAsso):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if abreviationAsso == 'pc' :
        form = Adhesion_permacatForm(request.POST or None)
    elif abreviationAsso == 'scic' :
        form = Adhesion_assoForm(abreviationAsso, request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('listeContacts', abreviationAsso)

    return render(request, 'asso/adhesion_ajouter.html', { "form": form,})

    return render(request, 'erreur.html', {'msg':"Désolé, il n'est pas encore possible d'adhérer a une autre asso par ce biais, réservé permacat"})

def creerAction_articlenouveau(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = creerAction_articlenouveauForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data["article"]
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(article.asso.abreviation))

            titre = "Nouvel article"
            message = "Un article a été posté dans le forum [" + str(
                article.asso.nom) + "] : '<a href='https://www.perma.cat" + article.get_absolute_url() + "'>" + article.titre + "</a>'"
            emails = [suiv.email for suiv in followers(suivi) if article.auteur != suiv and article.est_autorise(suiv)]
            if emails:
                action.send(article, verb='emails', url=article.get_absolute_url(), titre=titre, message=message, emails=emails)
            return redirect("bienvenue")
    else:
        form = creerAction_articlenouveauForm()

    return render(request, 'admin/creerAction_articlenouveau.html', { "form": form,})

