from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from actstream.models import Action, any_stream
from django.utils.timezone import now
from django.core.mail import send_mass_mail
from itertools import chain
from .forms import nouvelleDateForm
from .models import Profil
from .settings import SERVER_EMAIL, LOCALL, EMAIL_HOST_PASSWORD
from django_cron import CronJobBase, Schedule
from django.http import HttpResponseForbidden
from django.core.mail.message import EmailMultiAlternatives
import re

from django.core import mail

@login_required
def getNotifications(request, nbNotif=10, orderBy="-timestamp"):
    tampon = nbNotif * 5
    salons = Action.objects.filter(Q(verb='envoi_salon_Public')|Q(verb='envoi_salon_public'))
    articles = Action.objects.filter(Q(verb='article_nouveau') |Q(verb='article_nouveau_Public') | Q(verb='article_message_Public') |Q(verb='article_nouveau_public') | Q(verb='article_message_public') | Q(verb='article_modifier_Public')).order_by(orderBy)
    projets = Action.objects.filter(Q(verb='projet_nouveau') | Q(verb='projet_nouveau_Public') | Q(verb='projet_message_Public')| Q(verb='projet_nouveau_public') | Q(verb='projet_message_public') | Q(verb='projet_modifier_Public')).order_by(orderBy)
    offres = Action.objects.filter(Q(verb='ajout_offre')|  Q(verb='ajout_offre_Public')).order_by(orderBy)
    suffrages = Action.objects.filter(Q(verb='suffrage_ajout_Public') | Q(verb='suffrage_ajout')).order_by(orderBy)

    if request.user.adherent_permacat:
        salons     = salons | Action.objects.filter((Q(verb__startswith='envoi_salon') & Q(verb__icontains='Permacat')) | (Q(verb__startswith='envoi_salon_permacat')))
        articles   = articles | Action.objects.filter((Q(verb__startswith='article') & Q(verb__icontains='Permacat')) | (Q(verb__startswith='article_permacat')))
        projets    = projets | Action.objects.filter((Q(verb__startswith='projet') & Q(verb__icontains='Permacat')) | Q(verb='projet_permacat'))
        offres     = offres | Action.objects.filter((Q(verb__startswith='ajout_offre') & Q(verb__icontains='Permacat') )| Q(verb='ajout_offre_permacat'))
        suffrages  = suffrages | Action.objects.filter((Q(verb__startswith='suffrage_ajout') & Q(verb__icontains='Permacat')) | Q(verb='suffrage_ajout_permacat'))

    if request.user.adherent_rtg:
        salons     = salons | Action.objects.filter(Q(verb__startswith='envoi_salon') & Q(verb__icontains='Ramene ta graine'))
        articles   = articles | Action.objects.filter(Q(verb__startswith='article') & Q(verb__icontains='Ramene ta graine'))
        projets    = projets | Action.objects.filter(Q(verb__startswith='projet') & Q(verb__icontains='Ramene ta graine'))
        offres     = offres | Action.objects.filter(Q(verb__startswith='ajout_offre') & Q(verb__icontains='Ramene ta graine'))
        suffrages  = suffrages | Action.objects.filter(Q(verb__startswith='suffrage_ajout') & Q(verb__icontains='Ramene ta graine'))

    if request.user.adherent_ame:
        salons     = salons | Action.objects.filter(Q(verb__startswith='envoi_salon') & Q(verb__icontains='Animal Mieux Etre'))
        articles   = articles | Action.objects.filter(Q(verb__startswith='article') & Q(verb__icontains='Animal Mieux Etre'))
        projets    = projets | Action.objects.filter(Q(verb__startswith='projet') & Q(verb__icontains='Animal Mieux Etre'))
        offres     = offres | Action.objects.filter(Q(verb__startswith='ajout_offre') & Q(verb__icontains='Animal Mieux Etre'))
        suffrages  = suffrages | Action.objects.filter(Q(verb__startswith='suffrage_ajout') & Q(verb__icontains='Animal Mieux Etre'))

    salons = salons.distinct().order_by(orderBy)[:tampon]
    articles = articles.distinct().order_by(orderBy)[:tampon]
    projets = projets.distinct().order_by(orderBy)[:tampon]
    offres = offres.distinct().order_by(orderBy)[:tampon]
    suffrages = suffrages.distinct().order_by(orderBy)[:tampon]

    fiches = Action.objects.filter(verb__startswith='fiche').order_by(orderBy)[:tampon]
    ateliers = Action.objects.filter(Q(verb__startswith='atelier')|Q(verb='')).order_by(orderBy)[:tampon]
    conversations = (any_stream(request.user).filter(Q(verb='envoi_salon_prive', )) | Action.objects.filter(
        Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username))).order_by(
        orderBy)[:nbNotif]

    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ][:nbNotif]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ][:nbNotif]

    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)][:nbNotif]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor ) ][:nbNotif]
    salons = [art for i, art in enumerate(salons) if i == 0 or not (art.description == salons[i-1].description and art.actor == salons[i-1].actor ) ][:nbNotif]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor ) ][:nbNotif]
    inscription = Action.objects.filter(Q(verb__startswith='inscript'))

    return salons, articles, projets, offres, conversations, fiches, ateliers, inscription, suffrages

@login_required
def getNotificationsParDate(request, limiter=True, orderBy="-timestamp"):
    actions = Action.objects.filter( \
            Q(verb='envoi_salon')| Q(verb__icontains='public')|Q(verb__icontains='Public')|
            Q(verb__startswith='fiche')|Q(verb__startswith='atelier')|
            Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)|
            Q(verb__startswith='inscription'))
    if request.user.adherent_permacat:
        actions = actions | Action.objects.filter(Q(verb__icontains='Permacat') | Q(verb__icontains='permacat'))
    if request.user.adherent_rtg:
        actions = actions | Action.objects.filter(Q(verb__icontains='Ramene ta graine'))
    if request.user.adherent_ame:
        actions = actions | Action.objects.filter(Q(verb__icontains='Animal Mieux Etre'))

    actions = actions.distinct().order_by(orderBy)

    if limiter:
        actions=actions[:100]
    actions = [art for i, art in enumerate(actions) if i == 0 or not (art.description == actions[i-1].description and art.actor == actions[i-1].actor ) ][:50]

    return actions

@login_required
def getNbNewNotifications(request):
    actions = getNotificationsParDate(request)
    actions = [action for action in actions if request.user.date_notifications < action.timestamp]

    return len(actions)


@login_required
def get_notifications_news(request):
    actions = getNotificationsParDate(request)
    actions = [action for action in actions if request.user.date_notifications < action.timestamp]
    return actions

def raccourcirTempsStr(date):
    new = date.replace("heures","h")
    new = new.replace("heure","h")
    new = new.replace("minutes","mn")
    new = new.replace("minute","mn")
    return new

@login_required
def notifications_news_regroup(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, suffrages = getNotifications(request, nbNotif=500)

    dicoTexte = {}
    dicoTexte['dicoarticles'] = {}
    for action in articles:
        if request.user.date_notifications < action.timestamp:
            clef = action.action_object.titre
            if not clef in dicoTexte['dicoarticles']:
                dicoTexte['dicoarticles'][clef] = [action, ]
            else:
                dicoTexte['dicoarticles'][clef].append(action)

    htmlArticles = ""
    for titre_article, actions in dicoTexte['dicoarticles'].items():
        htmlArticles += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlArticles += " <div class=''><span  style='font-variant: small-caps ;'>" + titre_article
        if "(Jardins Partagés)" in actions[0].description:
            htmlArticles += "</span> <small> &nbsp;(Jardins Partagés)</small>"
        else:
            htmlArticles += "</span>"
        htmlArticles +=" </div><ul style='list-style-type:none'>"

        for action in actions :
            htmlArticles += "<li>"
            if action.description.startswith("a réagi"):
                htmlArticles += "commenté par "
            elif action.description.startswith("a ajout"):
                htmlArticles += "créé par "
            elif action.description.startswith("a modif"):
                htmlArticles += "modifié par "
            else:
                htmlArticles +=  str(action.actor) + " " + action.description
            htmlArticles += str(action.actor) + "&nbsp;&nbsp;<small> (il y a " + raccourcirTempsStr(
                action.timesince()) + ")</small></li>"

        htmlArticles += " </ul></a></li>"


    dicoTexte['dicoprojets'] = {}
    for action in projets:
        if request.user.date_notifications < action.timestamp:
            clef = action.action_object.titre
            if not clef in dicoTexte['dicoprojets']:
                dicoTexte['dicoprojets'][clef] = [action, ]
            else:
                dicoTexte['dicoprojets'][clef].append(action)

    htmlProjets = ""
    for titre_projet, actions in dicoTexte['dicoprojets'].items():
        htmlProjets += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlProjets += " <div  class='' ><spanstyle='font-variant: small-caps ;'>" + titre_projet
        if "(Jardins Partagés)" in actions[0].description:
            htmlProjets += "</span> (Jardins Partagés)"
        else:
            htmlProjets += "</span>"
        htmlProjets += " </div><ul style='list-style-type:none'>"

        for action in actions:
            htmlProjets += "<li>"
            if action.description.startswith("a réagi"):
                htmlProjets += "commenté par "
            elif action.description.startswith("a ajout"):
                htmlProjets += "créé par "
            elif action.description.startswith("a modif"):
                htmlProjets += "modifié par "
            else:
                htmlProjets +=  str(action.actor) + " " + action.description
            htmlProjets += str(action.actor) + "&nbsp;&nbsp;<small> (il y a " + raccourcirTempsStr(
                action.timesince()) + ")</small></li>"
        htmlProjets += " </ul></a></li>"


    dicoTexte['listautres'] = []
    for action in list(chain(inscriptions, suffrages, conversations, salons, offres, ateliers, fiches,)):
        if request.user.date_notifications < action.timestamp:
            dicoTexte['listautres'].append(action)

    return render(request, 'notifications/notifications_last2.html', {'dico':dicoTexte, "htmlArticles":htmlArticles, "htmlProjets":htmlProjets})

@login_required
def notifications(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, suffrages = getNotifications(request)
    return render(request, 'notifications/notifications.html', {'salons': salons, 'articles': articles,'projets': projets, 'offres':offres, 'conversations':conversations, 'fiches':fiches, 'ateliers':ateliers, 'inscriptions':inscriptions, 'suffrages':suffrages})

@login_required
def notifications_news(request):
    actions = get_notifications_news(request)
    return render(request, 'notifications/notifications_last.html', {'actions':actions})


@login_required
def notificationsParDate(request):
    actions = getNotificationsParDate(request)
    return render(request, 'notifications/notificationsParDate.html', {'actions': actions, })

@login_required
def notificationsLues(request):
    request.user.date_notifications = now()
    request.user.save()
    return redirect('notifications_news')

def getInfosJourPrecedent(request, nombreDeJours):
    from datetime import datetime, timedelta
    timestamp_from = datetime.now().date() - timedelta(days=nombreDeJours)
    timestamp_to = datetime.now().date() - timedelta(days=nombreDeJours - 1)

    if request.user.adherent_permacat:
        articles    = Action.objects.filter(Q(verb='article_nouveau_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='article_nouveau_Permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='article_nouveau',timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='projet_nouveau_Permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |
                                            Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='ajout_offre_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='ajout_offre_Permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
    else:
        articles    = Action.objects.filter(Q(verb='article_nouveau', timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,) | Q(verb='article_modifier', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
    fiches = Action.objects.filter(verb__startswith='fiche')
    ateliers = Action.objects.filter(Q(verb__startswith='atelier')|Q(verb=''))
    conversations = (any_stream(request.user).filter(Q(verb='envoi_salon_prive', )) | Action.objects.filter(
        Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)))

    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor) ]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor) ]
    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ]
    conversations = [art for i, art in enumerate(conversations) if i == 0 or not (art.description == conversations[i-1].description and art.actor == conversations[i-1].actor ) ]

    return articles, projets, offres, fiches, ateliers, conversations

def getTexteJourPrecedent(nombreDeJour):
    if nombreDeJour == 0:
        return "Aujourd'hui"
    elif nombreDeJour == 1:
        return "Hier"
    elif nombreDeJour == 2:
        return "Avant-hier"
    else:
        return "Il y a " + str(nombreDeJour) + " jours"

@login_required
def dernieresInfos(request):
    info_parjour = []
    for i in range(15):
        info_parjour.append({"jour":getTexteJourPrecedent(i), "infos":getInfosJourPrecedent(request, i)})
    return render(request, 'notifications/notifications_news.html', {'info_parjour': info_parjour,})


def changerDateNotif(request):
    form = nouvelleDateForm(request.POST or None, )
    if form.is_valid():
        request.user.date_notifications = form.cleaned_data['date']
        request.user.save()
        return redirect('notifications_news')
    else:
        return render(request, 'notifications/date_notifs.html', {'form': form})


def getListeMailsAlerte():
    actions = Action.objects.filter(verb='emails')
    messagesParMails = {}
    for action in actions:
        for mail in action.data['emails']:
            if not mail in messagesParMails:
                messagesParMails[mail] = [{'messages': [action.data['message'], ]}, ]
            else:
                for x in messagesParMails[mail]:
                    listeMessages = [x['messages'] for x in messagesParMails[mail]]
                    if not action.data['message'] in str(listeMessages):
                        messagesParMails[mail].append({'messages': [action.data['message'], ]})


    listeMails = []
    for mail, messages in messagesParMails.items():
        titre = "[Permacat] Du nouveau sur Perma.Cat"
        try:
            pseudo = Profil.objects.get(email=mail).username
        except:
            pseudo = ""
        messagetxt = "Bonjour / Bon dia " + pseudo +", Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :\n"
        message = "<p>Bonjour / Bon dia " + pseudo +",</p><p>Voici les dernières nouvelles des pages auxquelles vous êtes abonné.e :</p><ul>"
        for mess in messages:
            for m in mess['messages']:
                message += "<li>" + m + "</li>"
                try:
                    r = re.search("htt(.*?)>", m).group(1)[:-1]
                    messagetxt += re.sub('<[^>]+>', '', m) + " : htt" + r+ "\n"
                except:
                    messagetxt += re.sub('<[^>]+>', '', m) + "\n"


        messagetxt += "\nFins Aviat !\n---------------\nPour voir toute l'activité sur le site, consultez les Notifications : https://permacat.herokuapp.com/notifications/activite/ \n" + \
                   "Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou consultez la FAQ : https://permacat.herokuapp.com/faq/) "
        message += "</ul><br>"
        message += "<p>Fins Aviat !</p><hr>" + \
                   "<p><small>Pour voir toute l'activité sur le site, consultez les <a href='https://permacat.herokuapp.com/notifications/activite/'>Notifications </a> </small>. " + \
                   "<small>Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou consultez la <a href='https://permacat.herokuapp.com/faq/'>FAQ</a>)</small></p>"

        listeMails.append((titre, messagetxt, message, SERVER_EMAIL, [mail,]))
    return listeMails

def supprimerActionsEmails():
    actions = Action.objects.filter(verb='emails')
    for action in actions:
        action.delete()

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
        EmailMultiAlternatives(subject, message, sender, recipient,
                               alternatives=[(html_message, 'text/html')],
                               connection=connection)
        for subject, message, html_message, sender, recipient in datatuple
    ]
    return connection.send_messages(messages)


def envoyerEmailsRequete(request):
    listeMails = getListeMailsAlerte()

    send_mass_html_mail(listeMails, fail_silently=False)
    supprimerActionsEmails()
    return redirect('voirEmails')

def envoyerEmails():
    listeMails = getListeMailsAlerte()

    print('Envoi des mails' + str(listeMails))
    send_mass_html_mail(listeMails, fail_silently=False)
    print('Suppression des alertes')
    supprimerActionsEmails()
    print('Fait')


# class EnvoiMailsCronJob(CronJobBase):
#     RUN_AT_TIMES = ['6:30']
#
#     schedule = Schedule(run_at_times=RUN_AT_TIMES)
#     code = 'bourseLibre.views_notifications.EnvoiMailsCronJob'    # a unique code
#
#     def do(self):
#         envoyerEmails()
