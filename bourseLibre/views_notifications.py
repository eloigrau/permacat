from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from actstream.models import Action, any_stream
from bourseLibre.constantes import Choix as Choix_global
from django.utils.timezone import now
from itertools import chain
from .forms import nouvelleDateForm
from .models import Profil
from .settings.production import SERVER_EMAIL, EMAIL_HOST_PASSWORD
from django.http import HttpResponseForbidden
from django.core.mail.message import EmailMultiAlternatives
from datetime import datetime, timedelta
import re
import pytz
from django.core import mail

@login_required
def getNotifications(request, nbNotif=10, orderBy="-timestamp"):
    tampon = nbNotif * 5
    salons = Action.objects.filter(Q(verb='envoi_salon') | Q(verb='envoi_salon_Public')|Q(verb='envoi_salon_public'))
    articles = Action.objects.filter(Q(verb='article_nouveau') | Q(verb='article_nouveau_Public') | Q(verb='article_message') | Q(verb='article_message_Public') |Q(verb='article_nouveau_public') | Q(verb='article_message_public') | Q(verb='article_modifier_Public')| Q(verb='article_modifier_public')| Q(verb='article_modifier')).order_by(orderBy)
    projets = Action.objects.filter(Q(verb='projet_nouveau') | Q(verb='projet_nouveau_Public') | Q(verb='projet_message')|Q(verb='projet_message_Public')| Q(verb='projet_nouveau_public') | Q(verb='projet_message_public') |Q(verb='projet_modifier') |  Q(verb='projet_modifier_Public')).order_by(orderBy)
    offres = Action.objects.filter(Q(verb='ajout_offre')|  Q(verb='ajout_offre_public')).order_by(orderBy)
    suffrages = Action.objects.filter(Q(verb='suffrage_ajout_public') | Q(verb='suffrage_ajout')).order_by(orderBy)
    albums = Action.objects.filter(Q(verb='album_nouveau_public')).order_by(orderBy)

    if request.user.adherent_pc:
        salons     = salons | Action.objects.filter((Q(verb__startswith='envoi_salon') & Q(verb__icontains='Permacat')) | (Q(verb__startswith='envoi_salon_permacat')| (Q(verb__startswith='envoi_salon_pc'))))
        articles   = articles | Action.objects.filter(Q(verb__startswith='article') & (Q(verb__icontains='Permacat') | Q(verb__icontains='permacat')| Q(verb__icontains='pc')))
        projets    = projets | Action.objects.filter(Q(verb__startswith='projet') & (Q(verb__icontains='Permacat') | Q(verb__icontains='permacat')| Q(verb__icontains='pc')))
        offres     = offres | Action.objects.filter((Q(verb__startswith='ajout_offre') & Q(verb__icontains='Permacat') )| Q(verb='ajout_offre_permacat')| Q(verb='ajout_offre_pc'))
        suffrages  = suffrages | Action.objects.filter((Q(verb__startswith='suffrage_ajout') & Q(verb__icontains='Permacat')) | Q(verb='suffrage_ajout_permacat')| Q(verb='suffrage_ajout_pc'))
        albums = albums | Action.objects.filter(Q(verb='album_nouveau_pc')).order_by(orderBy)

    for nomAsso in Choix_global.abreviationsAsso:
        if getattr(request.user, "adherent_" + nomAsso):
            salons = salons | Action.objects.filter(Q(verb__startswith='envoi_salon') & Q(verb__icontains=nomAsso))
            articles = articles | Action.objects.filter(Q(verb__startswith='article') & Q(verb__icontains=nomAsso))
            projets = projets | Action.objects.filter(Q(verb__startswith='projet') & Q(verb__icontains=nomAsso))
            offres = offres | Action.objects.filter(Q(verb__startswith='ajout_offre') & Q(verb__icontains=nomAsso))
            albums = albums | Action.objects.filter(Q(verb__startswith='album_nouveau') & Q(verb__icontains=nomAsso))

    salons = salons.distinct().order_by(orderBy)[:tampon]
    articles = articles.distinct().order_by(orderBy)[:tampon]
    projets = projets.distinct().order_by(orderBy)[:tampon]
    offres = offres.distinct().order_by(orderBy)[:tampon]
    suffrages = suffrages.distinct().order_by(orderBy)[:tampon]
    albums = albums.distinct().order_by(orderBy)[:tampon]

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
    albums = [art for i, art in enumerate(albums) if i == 0 or not (art.description == albums[i-1].description and art.actor == offres[i-1].actor ) ][:nbNotif]
    inscription = Action.objects.filter(Q(verb__startswith='inscript'))

    return salons, articles, projets, offres, conversations, fiches, ateliers, inscription, suffrages, albums

@login_required
def getNotificationsParDate(request, limiter=True, orderBy="-timestamp"):

    actions = Action.objects.filter( \
         Q(verb='article_nouveau') | Q(verb='article_message')|
         Q(verb='article_modifier')|Q(verb='projet_nouveau') |
         Q(verb='projet_message')| Q(verb='projet_modifier')|
            Q(verb='envoi_salon')| Q(verb__icontains='public')|Q(verb__icontains='Public')|
            Q(verb__startswith='fiche')|Q(verb__startswith='atelier')|
            Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)|
            Q(verb__startswith='inscription'))
    if request.user.adherent_pc:
        actions = actions | Action.objects.filter(Q(verb__icontains='Permacat') | Q(verb__icontains='permacat')| Q(verb__icontains='pc'))
    if request.user.adherent_rtg:
        actions = actions | Action.objects.filter(Q(verb__icontains='rtg'))
    if request.user.adherent_fer:
        actions = actions | Action.objects.filter(Q(verb__icontains='fer'))
    if request.user.adherent_gt:
        actions = actions | Action.objects.filter(Q(verb__icontains='gt'))

    actions = actions.order_by(orderBy).distinct()

    if limiter:
        actions=actions[:100]
    actions = [art for i, art in enumerate(actions) if i == 0 or not (art.description == actions[i-1].description and art.actor == actions[i-1].actor ) ][:50]


    return actions


@login_required
def get_notifications_news(request):
    actions = getNotificationsParDate(request)
    dateMin = request.user.date_notifications.date() if request.user.date_notifications.date() > datetime.now().date() - timedelta(days=15) else datetime.now().date() - timedelta(days=15)

    actions = [action for action in actions if dateMin < action.timestamp.date()]
    return actions

@login_required
def getNbNewNotifications_test(request):
    return len(get_notifications_news(request))

@login_required
def getNbNewNotifications(request):
    actions = getNotificationsParDate(request)
    dateMin = request.user.date_notifications.date() if request.user.date_notifications.date() > datetime.now().date() - timedelta(days=15) else datetime.now().date() - timedelta(days=15)

    actions = [action for action in actions if dateMin < action.timestamp]

    return len(actions)


def raccourcirTempsStr(date):
    new = date.replace("heures","h")
    new = new.replace("heure","h")
    new = new.replace("minutes","mn")
    new = new.replace("minute","mn")
    return new

@login_required
def notifications_news_regroup(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, suffrages, albums = getNotifications(request, nbNotif=500)

    dicoTexte = {}
    dicoTexte['dicoarticles'] = {}

    utc = pytz.UTC
    if "fromdate" in request.GET:
        dateMin = datetime.strptime(request.GET["fromdate"], '%d-%m-%Y').replace(tzinfo=utc)
    else:
        date7jours = (datetime.now() - timedelta(days=15)).replace(tzinfo=utc)
        dateMin = request.user.date_notifications if request.user.date_notifications > date7jours else date7jours

    for action in articles:
        if dateMin < action.timestamp:
            try:
                clef = "["+action.action_object.asso.nom+"] " + action.action_object.titre
            except:
                clef = action.action_object.titre
            if not clef in dicoTexte['dicoarticles']:
                dicoTexte['dicoarticles'][clef] = [action, ]
            else:
                dicoTexte['dicoarticles'][clef].append(action)

    htmlArticles = ""
    for titre_article, actions in dicoTexte['dicoarticles'].items():
        htmlArticles += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlArticles += " <div class=''><span  style='font-variant: small-caps ;'>"
        if "(Jardins Partagés)" in actions[0].description:
            htmlArticles += "[Jardins Partagés] &nbsp;"+ titre_article +"</span>"
        else:
            htmlArticles += titre_article+"</span>"
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
        if dateMin < action.timestamp:
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
    for action in list(chain(inscriptions, suffrages, conversations, salons, offres, ateliers, fiches, albums)):
        if dateMin < action.timestamp:
            dicoTexte['listautres'].append(action)

    return render(request, 'notifications/notifications_last2.html', {'dico':dicoTexte, "htmlArticles":htmlArticles, "htmlProjets":htmlProjets, "dateMin":dateMin})

@login_required
def notifications(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, suffrages, albums = getNotifications(request)
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
    timestamp_from = datetime.now().date() - timedelta(days=nombreDeJours)
    timestamp_to = datetime.now().date() - timedelta(days=nombreDeJours - 1)

    if request.user.adherent_pc:
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
    albums = Action.objects.filter(verb__startswith='album')
    ateliers = Action.objects.filter(Q(verb__startswith='atelier')|Q(verb=''))
    conversations = (any_stream(request.user).filter(Q(verb='envoi_salon_prive', )) | Action.objects.filter(
        Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)))

    articles = [art for i, art in enumerate(articles) if i == 0 or not (art.description == articles[i-1].description  and art.actor == articles[i-1].actor)]
    projets = [art for i, art in enumerate(projets) if i == 0 or not (art.description == projets[i-1].description and art.actor == projets[i-1].actor) ]
    offres = [art for i, art in enumerate(offres) if i == 0 or not (art.description == offres[i-1].description and art.actor == offres[i-1].actor) ]
    fiches = [art for i, art in enumerate(fiches) if i == 0 or not (art.description == fiches[i-1].description and art.actor == fiches[i-1].actor ) ]
    ateliers = [art for i, art in enumerate(ateliers) if i == 0 or not (art.description == ateliers[i-1].description and art.actor == ateliers[i-1].actor ) ]
    conversations = [art for i, art in enumerate(conversations) if i == 0 or not (art.description == conversations[i-1].description and art.actor == conversations[i-1].actor ) ]
    albums = [art for i, art in enumerate(albums) if i == 0 or not (art.description == albums[i-1].description and art.actor == albums[i-1].actor ) ]

    return articles, projets, offres, fiches, ateliers, conversations, albums

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
        date = form.cleaned_data['date']
        return redirect('/notifications/activite'+ "?fromdate=" + str(date.day) +"-" + str(date.month) + "-" + str(date.year))
        #return HttpResponseRedirect('notifications_news' + "?fromdate=" + date.day +"-" + date.month + "-" + date.year)
        #request.user.date_notifications = form.cleaned_data['date']
        #request.user.save()
        #return redirect('notifications_news')
    else:
        return render(request, 'notifications/date_notifs.html', {'form': form})


def getListeMailsAlerte():
    actions = Action.objects.filter(verb='emails')
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
                   "<small>Pour vous désinscrire des alertes mails, barrez les cloches sur le site (ou consultez la <a href='https://www.perma.cat/faq/'>FAQ</a>)</small></p>"

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
    actions = Action.objects.all()
    for action in actions:
        try:
            print(action)
        except:
            action.delete()

    return render(request, 'notifications/voirActions.html', {'actions': actions,})

def nettoyerHistoriqueAdmin(request):
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
    from jardinpartage.models import Article as Article_jardin
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
            liste.append(article)
    newList = []
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
            newList.append(article)
    return liste

def voir_articles_a_archiver(request):
    liste = get_articles_a_archiver()
    return render(request, 'notifications/voirArchivage.html',{'liste': liste})

def archiverArticles(request):
    for art in get_articles_a_archiver():
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


# class EnvoiMailsCronJob(CronJobBase):
#     RUN_AT_TIMES = ['6:30']
#     schedule = Schedule(run_every_mins=RUN_AT_TIMES)
#     #RUN_EVERY_MINS = 3  # every 2 hours
#     #schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'bourseLibre.views_notifications.EnvoiMailsCronJob'    # a unique code
#
#     def do(self):
#         envoyerEmails()
#         #envoyerEmailstest()
