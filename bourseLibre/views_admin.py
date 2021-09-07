from django.shortcuts import render, redirect
from actstream.models import Action, Follow
from .models import Profil, Conversation, Suivis
from .settings import LOCALL
from .settings.production import SERVER_EMAIL, EMAIL_HOST_PASSWORD
from django.http import HttpResponseForbidden
from django.core.mail.message import EmailMultiAlternatives
import re
from django.core import mail
from actstream import actions

def getListeMailsAlerte():
    actions = Action.objects.filter(verb='emails')
    print('Nb ctions : '+ str(len(actions)))
    messagesParMails = {}
    for action in actions:
        for mail in action.data['emails']:
            if not mail in messagesParMails:
                messagesParMails[mail] = [action.data['message'], ]
            else:
                for x in messagesParMails[mail]:
                    if not action.data['message'] in messagesParMails[mail]:
                        messagesParMails[mail].append(action.data['message'])


    listeMails = []
    for mail, messages in messagesParMails.items():
        titre = "[Permacat] Du nouveau sur Perma.Cat"
        try:
            pseudo = Profil.objects.get(email=mail).username
        except:
            pseudo = ""
        messagetxt = "Bonjour / Bon dia, Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :\n"
        message = "<p>Bonjour / Bon dia,</p><p>Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :</p><ul>"
        for m in messages:
            message += "<li>" + m + "</li>"
            try:
                r = re.search("htt(.*?)>", m).group(1)[:-1]
                messagetxt += re.sub('<[^>]+>', '', m) + " : htt" + r+ "\n"
            except:
                messagetxt += re.sub('<[^>]+>', '', m) + "\n"


        messagetxt += "\nFins Aviat !\n---------------\nPour voir toute l'activité sur le site, consultez les Notifications : https://www.perma.cat/notifications/activite/ \n" + \
                   "Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou consultez la FAQ : https://www.perma.cat/faq/) "
        message += "</ul><br><p>Fins Aviat !</p><hr>" + \
                   "<p><small>Pour voir toute l'activité sur le site, consultez les <a href='https://www.perma.cat/notifications/activite/'>Notifications </a> </small>. " + \
                   "<small>Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou supprimez  <a href='https://www.perma.cat/accounts/mesSuivis/'>vos abonnements</a> ou consultez la <a href='https://www.perma.cat/faq/'>FAQ</a>)</small></p>"

        listeMails.append((titre, messagetxt, message, SERVER_EMAIL, [mail,]))


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
            #print("follow supprimé " + action)
            action.delete()

    actions = Action.objects.all()

    return render(request, 'notifications/voirActions.html', {'actions': actions,})

def nettoyerHistoriqueAdmin(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    from django.contrib.admin.models import LogEntry
    actions = LogEntry.objects.all()
    for action in actions:
        action.delete()

    return render(request, 'notifications/voirActions.html', {'actions': actions,})


def get_articles_a_archiver():
    from blog.models import Article, Evenement
    from datetime import datetime, timedelta
    import pytz
    utc = pytz.UTC
    date_limite = utc.localize(datetime.today() - timedelta(days=90))
    articles = Article.objects.filter(estArchive=False)

    liste = []
    for article in articles:
        test = False
        if article.start_time:
            if article.start_time < date_limite:
                if article.end_time:
                    if article.end_time < date_limite:
                        test = True
                else:
                    test = True

        if test:
            liste.append(article)
    liste2 = []
    from jardinpartage.models import Article as Article_jardin, Evenement as Evenement_jardin
    articles = Article_jardin.objects.filter(estArchive=False)
    for article in articles:
        test = False
        if article.start_time:
            if article.start_time < date_limite:
                if article.end_time:
                    if article.end_time < date_limite:
                        test = True
                else:
                    test = True

        if test:
            liste2.append(article)
    liste3 = []
    for art in liste:
        eve = Evenement.objects.filter(start_time__lt=date_limite, article=art)
        for ev in eve:
            test = False
            if ev.end_time:
                if ev.end_time < date_limite:
                    test = True
            else:
                test = True
        if test:
            liste3.append(article)

    for art in liste2:
        eve = Evenement_jardin.objects.filter(start_time__lt=date_limite, article=art)
        for ev in eve:
            test = False
            if ev.end_time:
                if ev.end_time < date_limite:
                    test = True
            else:
                test = True
        if test:
            liste3.append(article)

    return liste, liste2, liste3

def voir_articles_a_archiver(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    liste, liste2, liste3 = get_articles_a_archiver()
    return render(request, 'notifications/voirArchivage.html',{'liste': liste, 'liste2': liste2, 'liste3': liste3})

def archiverArticles(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    liste, liste2, liste3 =  get_articles_a_archiver()
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
    return render(request, 'notifications/voirEmails.html', {'listeMails': listeMails,})

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
    connection = mail.get_connection(
        username=SERVER_EMAIL,
        password=EMAIL_HOST_PASSWORD,
        fail_silently=fail_silently,
    )
    messages = [
        EmailMultiAlternatives(subject, message, sender, to=[sender,],
                               bcc=recipient,
                               alternatives=[(html_message, 'text/html')],
                               connection=connection)
        for subject, message, html_message, sender, recipient in datatuple
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

def envoyerEmails():
    print('Récupération des mails')
    listeMails = getListeMailsAlerte()

    print('Envoi des mails' + str(listeMails))
    send_mass_html_mail(listeMails, fail_silently=False)
    print('Suppression des alertes')
    supprimerActionsEmails()
    #supprimerActionsStartedFollowing()
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