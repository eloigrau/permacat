from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from actstream.models import Action, any_stream
from django.utils.timezone import now
from itertools import chain
from .forms import nouvelleDateForm

@login_required
def getNotifications(request, nbNotif=10, orderBy="-timestamp"):
    tampon = nbNotif * 5

    if request.user.is_permacat:
        salons      = Action.objects.filter(Q(verb='envoi_salon') | Q(verb='envoi_salon_permacat')).order_by(orderBy)[:tampon]
        articles    = Action.objects.filter(Q(verb__startswith='article')).order_by(orderBy)[:tampon]
        projets     = Action.objects.filter(Q(verb__startswith='projet')).order_by(orderBy)[:tampon]
        offres      = Action.objects.filter(Q(verb='ajout_offre') | Q(verb='ajout_offre_permacat')).order_by(orderBy)[:tampon]
        votations      = Action.objects.filter(Q(verb='ajout_votation') | Q(verb='ajout_votation_permacat')).order_by(orderBy)[:tampon]
    else:
        salons      = Action.objects.filter(Q(verb='envoi_salon')).order_by(orderBy)[:tampon]
        articles    = Action.objects.filter(Q(verb='article_nouveau') | Q(verb='article_message')| Q(verb='article_modifier')).order_by(orderBy)[:tampon]
        projets     = Action.objects.filter(Q(verb='projet_nouveau') | Q(verb='projet_message')| Q(verb='projet_modifier')).order_by(orderBy)[:tampon]
        offres      = Action.objects.filter(Q(verb='ajout_offre')).order_by(orderBy)[:tampon]
        votations = []

    #fiches = Action.objects.filter(Q(verb='fiche_nouveau')|Q(verb='fiche_ajouter_atelier')|Q(verb='fiche_modifier')|Q(verb='fiche_atelier_modifier')|Q(verb='fiche_message'))[:tampon]
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

    return salons, articles, projets, offres, conversations, fiches, ateliers, inscription, votations

@login_required
def getNotificationsParDate(request, limiter=True, orderBy="-timestamp"):
    if request.user.is_permacat:
        actions      = Action.objects.filter( \
            Q(verb='envoi_salon')| Q(verb='envoi_salon_permacat')|
            Q(verb__startswith='article')|Q(verb__startswith='projet')|
            Q(verb__startswith='fiche')|Q(verb__startswith='atelier')|
            Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)|
            Q(verb__startswith='inscription')|Q(verb='votation_nouveau') \
        ).order_by(orderBy)
    else:
        actions      = Action.objects.filter(Q(verb='envoi_salon')|
                                             Q(verb='article_nouveau') | Q(verb='article_message')|
                                             Q(verb='article_modifier')|Q(verb='projet_nouveau') |
                                             Q(verb='projet_message')| Q(verb='projet_modifier')|
                                             Q(verb='ajout_offre')|Q(verb__startswith='fiche')|
                                             Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)|

                                             Q(verb__startswith='atelier')|Q(verb__startswith='inscript') |
                                                Q(verb='envoi_salon_prive', description="a envoyé un message privé à " + request.user.username)
        ).order_by(orderBy)

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
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, votations = getNotifications(request, nbNotif=500)

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
    for article, actions in dicoTexte['dicoarticles'].items():
        htmlArticles += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlArticles += " <span style='font-variant: small-caps ;'>" + article
        if "(Jardins Partagés)" in actions[0].description:
            htmlArticles += "</span> <small> &nbsp;(Jardins Partagés)</small>"
        else:
            htmlArticles += "</span>"
        htmlArticles +=" <ul style='list-style-type:none'>"

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
    for article, actions in dicoTexte['dicoprojets'].items():
        htmlProjets += "<li class='list-group-item'><a href='" + actions[0].data['url'] + "'>"
        htmlProjets += " <span style='font-variant: small-caps ;'>" + article
        if "(Jardins Partagés)" in actions[0].description:
            htmlProjets += "</span> (Jardins Partagés)"
        else:
            htmlProjets += "</span>"
        htmlProjets += " <ul style='list-style-type:none'>"

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
    for action in list(chain(inscriptions, votations, conversations, salons, offres, ateliers, fiches,)):
        if request.user.date_notifications < action.timestamp:
            dicoTexte['listautres'].append(action)

    return render(request, 'notifications/notifications_last2.html', {'dico':dicoTexte, "htmlArticles":htmlArticles, "htmlProjets":htmlProjets})

@login_required
def notifications(request):
    salons, articles, projets, offres, conversations, fiches, ateliers, inscriptions, votations = getNotifications(request)
    return render(request, 'notifications/notifications.html', {'salons': salons, 'articles': articles,'projets': projets, 'offres':offres, 'conversations':conversations, 'fiches':fiches, 'ateliers':ateliers, 'inscriptions':inscriptions, 'votations':votations})

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

    if request.user.is_permacat:
        articles    = Action.objects.filter(Q(verb='article_nouveau_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='article_nouveau',timestamp__gte = timestamp_from, timestamp__lte = timestamp_to,))
        projets     = Action.objects.filter(Q(verb='projet_nouveau_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) |Q(verb='projet_nouveau', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
        offres      = Action.objects.filter(Q(verb='ajout_offre', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,) | Q(verb='ajout_offre_permacat', timestamp__gte = timestamp_from,timestamp__lte = timestamp_to,))
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


