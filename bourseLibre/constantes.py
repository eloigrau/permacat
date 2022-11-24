from django.utils.translation import gettext_lazy as _

DEGTORAD=3.141592654/180

class Choix():
    #couleurs = {'aliment':'#D8C457','vegetal':'#4CAF47','service':'#BE373A','objet':'#5B4694'}
    #couleurs = {'aliment':'#80B2C0','vegetal':'#A9CB52','service':'#E66562','objet':'#D8AD57'}
    couleurs = {'aliment':'#e6f2ff','vegetal':'#e6ffe6','service':'#ffe6e6','objet':'#ffffe6', 'offresEtDemandes':'#f2c7f1'}
    typePrixUnite = (('kg', 'kg'), ('100g', '100g'), ('10g', '10g'),('g', 'g'),  ('un', 'unité'), ('li', 'litre'))

    choix = {
    'aliment': {
        'souscategorie': ('legumes', 'fruits', 'aromates', 'champignons', 'boisson', 'herbes', 'condiments', 'viande', 'poisson', 'boulangerie', 'patisserie', 'autre'),
        #'etat': (('frais', 'frais'), ('sec', 'sec'), ('conserve', 'conserve')),
        'type_prix': typePrixUnite,
    },
    'vegetal': {
        'souscategorie': ('plantes', 'graines', 'fleurs', 'jeunes plants', 'purins', 'autre', ),
        #'etat': (('frais', 'frais'), ('séché', 'séché')),
        'type_prix': typePrixUnite,
    },
    'service': {
        'souscategorie': ('jardinage',  'éducation', 'santé', 'bricolage', 'informatique', 'hebergement','cuisine','batiment', 'mécanique', 'autre'),
        #'etat': (('excellent', 'excellent'), ('bon', 'bon'), ('moyen', 'moyen'), ('naze', 'naze')),
        'type_prix': (('h', 'heure'), ('un', 'unité')),
    },
    'objet': {
        'souscategorie': ('jardinage', 'outillage', 'vehicule', 'multimedia', 'mobilier','construction','instrument','autre'),
        #'etat': (('excellent', 'excellent'), ('bon', 'bon'), ('moyen', 'moyen'), ('mauvais', 'mauvais')),
        'type_prix': typePrixUnite,
    },
    'offresEtDemandes': {
        'souscategorie': ('Liste', ),
        #'etat': (('frais', 'frais'), ('sec', 'sec'), ('conserve', 'conserve')),
        'type_prix': typePrixUnite,
    },
    }
    monnaies = (('don', 'don'), ('troc', 'troc'), ('pret', 'prêt'), ('G1', 'G1'), ('Soudaqui', 'Soudaqui'), ('SEL', 'SEL'), ('JEU', 'JEU'),  ('HE', 'heureEntraide'),  ('Autre', 'Négociable'))
    monnaies_nonquantifiables = ['don', 'troc', 'pret', 'SEl', 'Autre']

    ordreTri = ['date', 'categorie', 'producteur']
    distances = ['5', '10', '20', '30', '50', '100']

    #statut_adhesion = (('', '-----------'),
    #                 (0, _("Je souhaite devenir membre de l'association 'PermaCat' et utiliser le site")),
    #                (1, _("Je souhaite utiliser le site, mais ne pas devenir membre de l'association Permacat")),
     #               (2, _("Je suis déjà membre de l'association Permacat")))


    abreviationsAsso = ["pc", "rtg", "scic", "citealt", "viure", "bzz2022"]
    abreviationsNomsAsso = [("pc", 'PermaCat'), ("rtg", 'Ramène Ta Graine'), ("scic", "PermAgora"), ("citealt", "Cité Altruiste"), ("viure", "Viure"), ("bzz2022", "Bzzz 2022")]
    abreviationsNomsAssoEtPublic = [('public', "Public"), ] + abreviationsNomsAsso

    suivisPossibles = ["articles_public"] + ['articles_jardin', 'projets', 'produits', 'conversations', 'documents', 'albums', 'ateliers', 'suffrages', 'salon_accueil']
    suivisPossibles_groupes = [('public', "articles_public"),] + [(abreviation,"articles_"+abreviation) for abreviation in abreviationsAsso]

    nomSuivis = {"articles_"+abreviation:'Article "' + nom_asso + '" du forum' for abreviation, nom_asso in abreviationsNomsAsso}

    nomSuivis.update({ 'articles_public':'Articles "Public" du forum',
                       'articles': 'Article du forum',
                          'articles_jardin':'Article aux jardins partagés',
                          'projets':"Projet",
                          'produits':"Offre/demande à l'altermarché",
                          'conversations':"Message privé",
                          'documents': "Document téléchargeable",
                          'albums': "Album photo",
                          'ateliers': "Proposition d'Atelier",
                          'suffrages': "Suffrage (vote)",
                          'salon_accueil': "Salons de discussion publics",
                  })

    type_paiement_adhesion = ('0', 'Espèce'), ("1", "HelloAsso"), ("2", "Cheque"), ("3", "Virement")


