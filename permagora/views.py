from django.shortcuts import render, redirect, HttpResponseRedirect
from django.db.models import CharField
from django.db.models.functions import Lower
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.mail import mail_admins, send_mail, BadHeaderError
from .forms import ContactForm, SignerForm, MessageForm, CommentaireForm, PropositionCharteCreationForm, PropositionCharteChangeForm
from .models import Profil, Message_permagora, PoleCharte, PropositionCharte, Commentaire_charte, Vote, Signataire, GenericModel
from datetime import datetime, timedelta
from django.views.generic import ListView, UpdateView, DeleteView
from django.db.models import F
from django.http import HttpResponse
from actstream import action
from actstream.models import Action
from django.db.models import Q
from pytz import UTC as utc
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

CharField.register_lookup(Lower, "lower")


def handler404(request, template_name="404.html"):  #page not found
    response = render(request, "permagora/404.html")
    response.status_code = 404
    return response

def handler500(request, template_name="500.html"):   #erreur du serveur
    response = render(request, "permagora/500.html")
    response.status_code = 500
    return response

def handler403(request, template_name="403.html"):   #non autorisé
    response = render(request, "permagora/403.html")
    response.status_code = 403
    return response

def handler400(request, template_name="400.html"):   #requete invalide
    response = render(request, "permagora/400.html")
    response.status_code = 400
    return response

def bienvenue(request):
    commentaires = Message_permagora.objects.filter(type_article="5").order_by("date_creation")
    form = MessageForm(request.POST or None)

    obj, created = GenericModel.objects.get_or_create(type_article='5', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article = "5"
        comment.save()

        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page de bienvenue de l'Agora")
        return redirect(request.path)

    return render(request, 'permagora/bienvenue.html', { 'form': form, 'commentaires': commentaires})

def planSite(request):
    listeProp = PropositionCharte.objects.all()
    return render(request, 'permagora/planSite.html', { 'listeProp': listeProp,})

def presentation_site(request):
    return render(request, 'presentation_site.html')

def merci(request):
    return render(request, 'permagora/merci.html')

def faq(request):
    return render(request, 'permagora/faq.html')

def statuts(request):
    return render(request, 'permagora/statuts.html')

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
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            message_txt = request.user.username + " a envoyé le message suivant : "
            message_html = form.cleaned_data['msg']
            try:
                mail_admins(sujet, message_txt, html_message=message_html)
                if form.cleaned_data['renvoi']:
                    send_mail(sujet, message_txt, request.user.email, request.user.email, fail_silently=False, html_message=message_html)

                return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                       'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                       "destinataire": "administrateurs "})
            except BadHeaderError:
                return render(request, 'erreur.html', {'msg':'Invalid header found.'})

            return render(request, 'permagora/erreur.html', {'msg':"Désolé, une ereur s'est produite"})
    else:
        form = ContactForm()
    return render(request, 'permagora/contact.html', {'form': form, "isContactProfil":False})


def contact_admins(request):
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            message_txt = request.user.username + " a envoyé le message suivant : "
            message_html = form.cleaned_data['msg']
            try:
                mail_admins(sujet, message_txt, html_message=message_html)
                if form.cleaned_data['renvoi']:
                    send_mail(sujet, message_txt, request.user.email, request.user.email, fail_silently=False, html_message=message_html)

                return render(request, 'message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                       'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                       "destinataire": "administrateurs "})
            except BadHeaderError:
                return render(request, 'erreur.html', {'msg':'Invalid header found.'})

            return render(request, 'permagora/erreur.html', {'msg':"Désolé, une ereur s'est produite"})
    else:
        form = ContactForm()
    return render(request, 'permagora/contact.html', {'form': form, "isContactProducteur":False})

def cgu(request):
    return render(request, 'permagora/cgu.html', )

def fairedon(request):
    return render(request, 'permagora/fairedon.html', )

@login_required
def statistiques(request):
    nb_inscrits = Profil.objects.all().count()
    return render(request, 'permagora/statistiques.html', {"nb_inscrits":nb_inscrits})

@login_required
def signataires(request):
    signataires = Signataire.objects.all()
    nb_total_signe = signataires.count()
    signataires_visibles = signataires.filter(apparait_visible=True)
    return render(request, 'permagora/signataires.html', {"signataires":signataires_visibles, "nb_total_signe":nb_total_signe})


def liens(request):
    liens = [
        'https://jancovici.com/',
        'https://alternatiba.eu/alternatiba66/',
        'https://colibris-universite.org/mooc-permaculture/wakka.php?wiki=PagePrincipale',
    ]
    #commentaires = Message.objects.filter(type_article="4", valide=True).order_by("date_creation")
    commentaires = Message_permagora.objects.filter(type_article="4").order_by("date_creation")
    form = MessageForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article="4"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page de liens de l'Agora")
        return redirect(request.path)

    return render(request, 'permagora/liens.html', {'liens':liens, 'form': form, 'commentaires': commentaires})


def preambule(request):
    commentaires = Message_permagora.objects.filter(type_article="6").order_by("date_creation")
    form = MessageForm(request.POST or None)
    obj, created = GenericModel.objects.get_or_create(type_article='6', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article = "6"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page de préambule de l'Agora")
        return redirect(request.path)
    return render(request, '0_preambule.html', {'form': form, 'commentaires': commentaires}, )

def introduction(request):
    commentaires = Message_permagora.objects.filter(type_article="0").order_by("date_creation")
    form = MessageForm(request.POST or None)
    obj, created = GenericModel.objects.get_or_create(type_article='0', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article="0"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page d'introduction de l'Agora")
        return redirect(request.path)

    return render(request, '1_introduction.html', {'form': form, 'commentaires': commentaires}, )

def risques(request):
    dico_risques = [
        ("Ressources en berne :", "<ol><li>l'eau en danger: nappes phréatiques en net recul, polluées et salinisées, précipitations en forte diminution, assèchement des cours d'eau et des sols, </li><li> les sols pollués/détruits par l'agro-industrie, </li><li> l'approvisionnement énergétique en danger (principalement le pétrole et le gaz), \
        </li><li> approvisionnement en nourriture en danger (perte du secteur agricole local, diminution des rendements) </li><li> matériaux de construction importés, sans filières locales écologiques efficientes (bois, chanvre, briques, sable de construction, matériaux comme le cuivre qui s'épuise, etc)</li></ol>"),
        ("Risques naturels importants", "<ol> <li> érosion des sols, </li>  <li> érosion du trait de cote, </li><li> inondations, </li><li> sécheresses,  </li><li>canicules,  </li><li>incendies. </li></ol>" \
                              "<p>Tous ces risques augmentent considérablement et de façon non-linéaire (par paliers et donc 'crises') à cause du changement climatique</p>"),
        ("Agriculture en danger ", "disparition des terres agricoles, perte de rendements, disparition/pollution/salinisation de l'eau, sécheresses répétitives, perte des pollinisateurs de la biodiversité qui est nécessaire à l'agriculture. Modèle économique mondialisé, polluant, émetteur de CO2, dépendant du pétrole, appauvrissant la grande majorité des agriculteurs, et proche du krach."),
        ("Economie malade ", "seul le tourisme de masse et 'l'économie résidentielle' semblent être mis en valeur, détruisant ainsi nos nappes, folklorisant notre identité, ne créant que peu d'emplois et souvent saisonniers, à faible valeur ajoutée. Un fort trafic (encore du pétrole) dû à la métropolisation de Perpignan et l’éloignement des zones d'habitation avec les zones commerciales. Chômage massif, et travail au noir généralisé sont le lot de notre département."),
        ("Aménagement du territoire inapproprié", " nos paysages sont modifiés par l'Homme de façon désordonnée, irresponsable et inadaptée aux futures crises, par <ol><li> l’appât du gain à court terme (champs d’éoliennes qui défigurent nos paysages sans être une réelle solution écologique, construction sur des terres agricoles fertiles, extension des grands centres commerciaux totalement inadaptés en cas de crise pétrolière, etc), sans parler de la corruption de nos 'élites locales', </li><li> la démographie excessive, sans contrôle du foncier </li><li> Un réseau de transport entièrement pensé avec un pétrole abondant, donc très vulnérable et polluant."),
        ("Une démocratie en berne", "Le système électoral a perdu de sa crédibilité. Il efface une grande partie de la population, et n'est plus adapté aux enjeux actuels. L'interet collectif semble oublié. Les citoyens se sont vus dépossédés de leur pouvoir au profit d'un système clanique. IL est temps que les citoyens retrouvent leur juste place dans les décisions qui les concernent."),
        ("Identité effacée", " perte de notre culture catalane, de notre patrimoine culturel, artistique et linguistique. Ainsi c'est toute la cohésion du territoire qui est mise à mal. Sans reconnaissance de notre identité, il ne peut y avoir de solidarité, de projet commun et in fine d'organisation politique démocratique locale. Sans identité collective propre, point de salut collectif."),
        ("Dépendance vis-à-vis de l’extérieur ", " approvisionnement en ressources (pétrole, matériaux de construction, etc), monnaie sous contrôle des banques et des industries polluantes et émettrices de CO2, décisions politiques centralisées hors de nos frontières et de notre contrôle, etc."),
    ]
    commentaires = Message_permagora.objects.filter(type_article="1").order_by("date_creation")
    obj, created = GenericModel.objects.get_or_create(type_article='1', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article = "1"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page du constat de l'Agora")
        return redirect(request.path)

    return render(request, '2_risques.html', {"dico_risques":dico_risques, 'form': form, 'commentaires': commentaires})

def preconisations(request):
    dico_risques = [ ("Soutien à l'agriculture (biologique et permacole) ",
                      " tous les agriculteurs doivent a minima passer en bio, et les collectivités doivent aider à la mise en place de fermes agro-écologiques ou à défaut de jardins partagés. Ce sont des lieux individualisés ou collectifs de production (agricole et artisanale) qui peuvent : <ol><li> fournir de la nourriture locale et saine </li><li> gérer l'eau de façon durable </li><li> fournir du travail aux gens d'ici </li><li> gérer les stock de bois (énergie renouvelable et construction), </li><li> maintenir la biodiversité indispensable à notre survie, </li><li>créer du lien social, </li><li> optimiser l'usage des ressources, </li><li> être des lieux d'éducation, de formation et de citoyenneté.</li></ol>Il est aussi nécessaire de lutter contre tous les pesticides et engrais chimiques (qui dépendent aussi du pétrole, et qui polluent durablement nos sols et notre eau), et cela passe obligatoirement par des fermes agro-écologiques qui par leur multiples activités (élevage, maraichage, foresterie, etc) sont plus résilientes et peuvent amener des solutions alternatives aux pesticides et engrais."),

    ("Reforestation",
        "La reforestation du territoire doit être commencée au plus vite, en restaurant toutes les haies, les corridors écologiques (trame verte et bleue, etc), et en plantant des forêts mixtes (fruitiers et non-fruitiers), y compris en zones urbaines. Les arbres sont un atout majeur et indispensable : ils apportent des fruits, du fourrage, de l'énergie renouvelable, stockent du carbone, créent des milieux favorables pour la faune et la flore (protection des oiseaux, des insectes, et de toute la chaine alimentaire), protègent les champignons, apportent de l'humus, protègent de l'évaporation et donc de la sécheresse mais aussi des inondations, apportent de l'ombre, et font remonter les minéraux et l'eau du sous-sol par leur système racinaire. Par ailleurs, il faut repenser la place des animaux dans notre société, dont une partie doit être traitée éthiquement (l'élevage non intensif) et une partie doit rester sauvage (protection renforcée des réserves naturelles) pour que le système agro-écologique soit résilient. Les races endémiques de notre région doivent être protégées (chèvre et vach de l'Albère, âne des pyrenées, etc.)"),
     ("Economie",
      "Le développement économique doit être re-pensé en incluant des limites : limites d'usage du sol, d'usage du pétrole, limite de la démographie, limite d'arrosage et de précipitations. Refonder l'économie autour de l'agriculture est une solution possible. Le développement d'alternatives à la monnaie-dette 'euro' doit être encouragé et progressivement développé, pour se protéger d'une crise économique majeure de la zone euro (qui ne saurait tarder selon toute vraisemblance). La solution passe par l'utilisation croissante du Soudaqui (monnaie locale adossée à l'euro, pour l'instant), du J.E.U. ou de la Monnaie Libre (monnaie sur internet basée sur la technologie de la 'blockchain''), dans une économie locale circulaire et équitable, notamment en payant une partie des salaires des fonctionnaires et élus locaux en monnaie alternative. Mais aussi en les utilisant dans les coopératives agricoles et les différentes filières restaurées ou crées ad hoc  (bois/énergie, paille/fourrage/construction, briques/construction. etc.)" ),
     ("Création d'assemblées citoyennes ", "pour informer, débattre, créer du lien, s'organiser localement sans attendre que les autres le fassent pour nous. Pour résoudre aussi les conflits qui vont se multiplier entre nous (la justice française n'est plus à la hauteur, et de plus en plus débordée et inefficace). Chaque commune doit pouvoir créer à sa façon des assemblées régulières et ayant un certain pouvoir sur les prises de décision au nom de la commune. Il est nécessaire d'impliquer toutes les bonnes volontés, et la population dans son ensemble doit pouvoir participer. Il s'agit d'inventer de nouvelles formes de gouvernance qui tiennent compte des enjeux et aspirations de notre époque. Cela va de pair avec la formation et l'éducation de la jeunesse, et de la population en général, aux enjeux écologiques, économiques, politiques et sociaux."),
     ("Créer des médias/réseaux sociaux locaux ", " Des plateformes open-source et libres comme www.perma.cat, ou bien des médias locaux (par exemple 'La Clau') peuvent être des exemples ou une base, qui permettent de s'affranchir des GAFAM (Google Amazon Facebook, Apple, Microsoft), immenses pollueurs, et outils puissants de contrôle de la population à notre insu, et d'avoir une information locale plurielle, démocratique et utile à notre cohésion."),
     ("Education ", "intégrer dans les cursus scolaires (collèges, lycées,  université) et peri-scolaires des temps d'apprentissage autour des enjeux des bouleversements contemporains (climat, ressources, biodiversité...)."),
     ("Formation ", "partage des savoirs autour de la gouvernance partagée, de la permaculture, des 'low technologies' (techniques non-industrielles et bas carbone que chacun peut se réapproprier car nécessitant peu de pétrole et peu de connaissances spécialisées : four solaire, compostage, velorution, etc)"),
     ("Gestion de l'eau", "réduction drastique de l'usage de l'eau pour préserver nos nappes phréatiques : toilettes sèches et récupération des eaux grises et des eaux de pluie. restauration des canaux historiques pour l'agriculture, création de retenues collinaires pour stocker les pluies, contrôle des forages, interdiction d'arroser les pelouses et limitation des piscines."),
     ("Gestion des ressources", "limitation prévisionnelle des usages  (industries, transport, domestique) de l'énergie notamment, afin d'anticiper leur diminution d'approvisionnement. Laisser une place aux ressources naturelles sans intervention humaine afin de laisser la biodiversité s'auto réguler et s'adapter au changement climatique")
    ]

    commentaires = Message_permagora.objects.filter(type_article="2").order_by("date_creation")
    obj, created = GenericModel.objects.get_or_create(type_article='2', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article = "2"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page des préconisations de l'Agora")
        return redirect(request.path)

    return render(request, '3_preconisations.html', {"dico_risques":dico_risques, 'form': form, 'commentaires': commentaires})


dico_charte =[
    ("Promouvoir l'agriculture",
  ("Aider à la création de fermes agro-ecologiques",
   "Interdire tous les pesticides dans la commune",
   "Replanter les haies et créer des espaces arborés",
   "Que les cantines scolaires soient fournies de plus en plus par l'agriculture locale biologique ou permacole",
   "Faire un jardin potager au sein des établissements scolaires en lien avec les maraichers locaux",
   "Favoriser l'agriculture biologique et la permaculture dans ma commune",
   "Soutenir ou aider à la création de jardins partagés, ou jardins familiaux",
   "Soutenir ou aider à la création de coopératives agricoles",
  ),),

  ("Préserver les ressources",
   ("Limiter l'usage de l'eau au strict minimum",
    "Penser les transports du futur pour économiser l'energie: <ol><li> mobilité douce (vélo, traction animale, bateaux),</li><li>transports en commun (bus, taxi collectifs, espaces dédiés au covoiturage au sein de la commune, etc).</li><li>nouvelles technologies : bornes de rechargement pour les véhicules électriques, à partir d'énergie renouvelable et locale. Usine d'hydrogène, centrales solaires (thermiques et électriques), etc.</li></ol>",
    "Encourager la création d'une filière bois/énergie locale et durable",
    "Encourager la création d'une filière solaire et d'énergies renouvelables locale et durable",
    "Arrêter toute artificialisation des terres (n'accepter aucun nouveaux projet de construction qui ne soit pas vraiment eco-responsable)"
    "Limiter l'éclairage urbain pendant la nuit (pollution lumineuse, dépense énergétique peu utile)"
    ),),

 ("Développer l'économie locale en tenant compte de l'environnement en priorité",
  ("Préserver et valoriser notre patrimoine culturel, foncier et historique",
   "Aider au déploiement des monnaies alternatives",
   "Participer à la création de filières locales, en créant de l'économie circulaire",
   "Aider à la création de syndicats et coopératives agricoles citoyennes",
   "Créer une caisse de solidarité pour indemniser les victimes des futures catastrophes naturelles (pourquoi pas en monnaie alternative ?)",
   "Encourager le tourisme éco-responsable, et limiter les activités touristiques polluantes ou consommatrices  d'eau (golf, piscine privées, etc)",
   ),),

 ("Urbaniser intelligemment",
 ("Préserver notre identité paysagère, respecter notre patrimoine architectural",
  "Végétaliser, reboiser, replanter les haies", "préserver les canaux d'arrosage",
  "Intégrer les activités agricoles dans la vie des villes et villages",
  "Utiliser des espaces pour organiser des lieux de vie et des assemblées collectifs",
  "Contrôler le foncier en n'oubliant pas d'intégrer les logements sociaux aux activités économiques",
  "Limiter l'étalement urbain", " favoriser les habitats légers, ou eco-responsables", "aménager des voies cyclables et de covoiturage",
  "Laisser de la place pour la faune et la flore sauvage",
  "Prendre soin des cours d'eau, et des canaux d'irrigation"),
  ),
  ("Contrôler la démographie ",
  ( "Limiter le tourisme de masse à basse valeur ajoutée en imposant des normes écologiques (par exemple taxer les ordures au delà d'un certain seuil, ou imposer un 'visa touristique' qui permette de traiter les dégats écologiques du tourisme)",
    "Contrôler le foncier",
    "Densifier les zones d'habitat",
    "Intégrer les nouveaux arrivants en les sensibilisant aux questions écologiques, politiques, économiques et identitaire.",
    "Inclure les personnes âgées dans les activités de la commune, notamment pour animer les assemblées locales.",
    "Accueillir dignement les migrants, du nord ou du sud, en les faisant participer à la vie des communes, notammant dans les activités des fermes agro-écologiques", ),
   ),
 ("Respecter notre identité et encourager la  citoyenneté",
 ("Adopter la signalétique de la commune (nom des voies, monuments, affiches, etc) en catalan",
  "Respecter les traditions séculaires catalanes",
  "Favoriser le bilinguisme au sein des établissements scolaires",
  "Favoriser le bilinguisme au sein de la mairie et des actes publics",
  "Créer des assemblées locales citoyennes pour informer et débattre autour des enjeux du changement climatique et de la fin du pétrole.",
  "Proposer des salles pour développer le domaine associatif local",
  "Créer du lien et de la solidarité entre catalans (habitants et sympathisants du Pays Catalan)",
  ),)
]

def propositions(request):
    commentaires = Message_permagora.objects.filter(type_article="3").order_by("date_creation")
    obj, created = GenericModel.objects.get_or_create(type_article='3', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article="3"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page des propositions de l'Agora")
        return redirect(request.path)
    dico_charte = ((pole, (prop for prop in PropositionCharte.objects.filter(pole=pole).order_by("id"))) for pole in PoleCharte.objects.all().order_by("id") if PropositionCharte.objects.filter(pole=pole))
    return render(request, 'permagora/propositions.html', {"dico_charte":dico_charte, 'form': form, 'commentaires': commentaires})


def organisationPermagora(request, ):
    commentaires = Message_permagora.objects.filter(type_article="7").order_by("date_creation")
    obj, created = GenericModel.objects.get_or_create(type_article='7', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article = "7"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page de l'organisation de l'Agora")
    return render(request, 'permagora/organisationPermagora.html', {'form': form, 'commentaires': commentaires})

def presentationPermagora(request, ):
    commentaires = Message_permagora.objects.filter(type_article="6").order_by("date_creation")
    obj, created = GenericModel.objects.get_or_create(type_article='6', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.type_article="6"
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=comment, url=comment.get_absolute_url() + "#idConversation",
                     description="a commenté la page de la présentation de PermAgora")

    return render(request, 'permagora/presentationPermagora.html', {'form': form, 'commentaires': commentaires})

@login_required
def profil_courant(request, ):
    return render(request, 'permagora/profil.html', {'user': request.user})


@login_required
def profil(request, user_id):
    try:
        user = Profil.objects.get(id=user_id)
        distance = user.getDistance(request.user)
        return render(request, 'permagora/profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
            return render(request, 'permagora/profil_inconnu.html', {'userid': user_id})

@login_required
def profil_nom(request, user_username):
    try:
        user = Profil.objects.get(username=user_username)
        distance = user.getDistance(request.user)
        return render(request, 'profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
        return render(request, 'profil_inconnu.html', {'userid': user_username})

@login_required
def signer(request):
    form_signer = SignerForm(request.POST or None)
    if form_signer.is_valid():
        signataire, cree = Signataire.objects.get_or_create(auteur=request.user)
        signataire.apparait_visible = form_signer.cleaned_data['apparait_visible']
        signataire.save()
        return render(request, 'permagora/merci.html')

    return render(request, 'permagora/signer.html', {"form_signer": form_signer, })

@login_required
def designer(request):
    signataire = Signataire.objects.filter(auteur=request.user)
    signataire.delete()
    return redirect("permagora:profil_courant")


def ajouterPoleCharte(request):
    for domaine in dico_charte:
        domaine_obj, created = PoleCharte.objects.get_or_create(titre=domaine[0])
        for message in domaine[1]:
            proposition, created = PropositionCharte.objects.get_or_create(titre=message, domaine=domaine_obj)
    return render(request, 'permagora/merci.html')

def voirProposition(request, slug):
    proposition = PropositionCharte.objects.get(slug=slug)
    obj, created = GenericModel.objects.get_or_create(type_article='3', message=proposition.slug)
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    commentaires = Commentaire_charte.objects.filter(proposition=proposition)
    if request.user.is_authenticated:
        vote, created = Vote.objects.get_or_create(auteur=request.user, proposition=proposition)
    else:
        vote = None
    form = CommentaireForm(request.POST or None)
    if form.is_valid():
        if not request.user.is_authenticated:
            return redirect('login')
        comment = form.save(commit=False)
        comment.auteur = request.user
        comment.proposition = proposition
        comment.save()
        action.send(request.user, verb='permagora_commentaire', action_object=proposition, url=proposition.get_absolute_url(),
                     description="a commenté la page de la proposition %s " % proposition.titre)
        return redirect(request.path)
    return render(request, 'permagora/voirProposition.html', {'form': form, 'proposition':proposition, 'commentaires':commentaires, 'vote':vote})

def ajouterVote_plus(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    proposition = PropositionCharte.objects.get(slug=slug)
    vote, created = Vote.objects.get_or_create(auteur=request.user, proposition=proposition)
    if vote.type_vote == "0" :
        vote.type_vote = "1"
        proposition.compteur_plus=proposition.compteur_plus + 1
    elif vote.type_vote == "1":
        vote.type_vote = "0"
        proposition.compteur_plus=proposition.compteur_plus - 1
    elif vote.type_vote == "2":
        vote.type_vote = "1"
        proposition.compteur_plus=proposition.compteur_plus + 1
        proposition.compteur_moins=proposition.compteur_moins - 1
    proposition.save()
    vote.save()
    return redirect(request.GET['next'])


def ajouterVote_moins(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    proposition = PropositionCharte.objects.get(slug=slug)
    vote, created = Vote.objects.get_or_create(auteur=request.user, proposition=proposition)
    if vote.type_vote == "0":
        vote.type_vote = "2"
        proposition.compteur_moins=proposition.compteur_moins + 1
    elif vote.type_vote == "1":
        vote.type_vote = "2"
        proposition.compteur_plus=proposition.compteur_plus - 1
        proposition.compteur_moins=proposition.compteur_moins + 1
    elif vote.type_vote == "2":
        vote.type_vote = "0"
        proposition.compteur_moins=proposition.compteur_moins- 1
    proposition.save()
    vote.save()
    return redirect(request.GET['next'])


@login_required
def ajouterProposition(request):
    form = PropositionCharteCreationForm(request, request.POST or None)
    time_threshold = datetime.now() - timedelta(hours=24)
    props = PropositionCharte.objects.filter(auteur=request.user, date_creation__gt=time_threshold)
    NBMAX_ARTICLES = 20
    if not request.user.is_superuser and len(props) > NBMAX_ARTICLES:
        return render(request, 'erreur2.html', {"msg": "Vous avez déjà posté %s propositions depuis 24h, veuillez patienter un peu avant de poster un nouvel article, merci !"% NBMAX_ARTICLES})

    if form.is_valid():
        prop = form.save(request.user)
        #url = article.get_absolute_url() + "#ref-titre"
        #suffix = "_" + article.asso.abreviation
        #action.send(request.user, verb='article_nouveau'+suffix, action_object=article, url=url,
        #           description="a ajouté un article : '%s'" % article.titre)
        action.send(request.user, verb='permagora_ajoutProposition', action_object=prop, url=prop.get_absolute_url(),
                     description="a ajouté  la proposition %s " % prop.titre)
        return redirect(prop.get_absolute_url())

    return render(request, 'permagora/ajouterProposition.html', { "form": form, })


class ModifierProposition(UpdateView):
    model = PropositionCharte
    form_class = PropositionCharteChangeForm
    template_name_suffix = '_modifier'

    def form_valid(self, form):
        self.object = form.save(sendMail=False, commit=True, )
        # self.object.date_modification = now()
        # self.object.save(sendMail=form.changed_data!=['estArchive'])
        # url = self.object.get_absolute_url()
        # suffix = "_" + self.object.asso.abreviation
        # if not self.object.estArchive:
        #     if self.object.date_modification - self.object.date_creation > timedelta(minutes=10):
        #         action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
        #                      description="a modifié l'article [%s]: '%s'" %(self.object.asso, self.object.titre))
        # elif form.changed_data == ['estArchive']:
        #     action.send(self.request.user, verb='article_modifier'+suffix + "-archive", action_object=self.object, url=url,
        #                  description="a archivé l'article [%s]: '%s'" %(self.object.asso, self.object.titre))

        #envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierProposition, self).get_form(*args, **kwargs)
        return form


@login_required
def voirNotifications(request, ):
    dateMin = (datetime.now() - timedelta(days=100)).replace(tzinfo=utc)
    actions = Action.objects.filter(Q(timestamp__gt=dateMin) & Q(verb__startswith='permagora_')).order_by("-timestamp")
    return render(request, 'permagora/voirNotifications.html', { "actions": actions, })

