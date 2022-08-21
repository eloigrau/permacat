from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from bourseLibre.constantes import Choix
from bourseLibre.models import Asso
import random
import string

register = template.Library()

class Constantes:
    typesAvecEntete = ['Select', " NumberInput", "DateInput","DateTimeInputWidget", "SummernoteWidget", "CheckboxSelectMultiple" ]#'Textarea',
    width = 10
    dicoMois = {"January".center(width): "Janvier".center(width), "February".center(width): "Février".center(width),
                "March".center(width): "Mars".center(width), "April".center(width): "Avril".center(width),
                "May".center(width): "Mai".center(width), "June".center(width): "Juin".center(width),
                "July".center(width): "Juillet".center(width), "August".center(width): "Août".center(width),
                "September".center(width): "Septembre".center(width), "October".center(width): "Octobre".center(width),
                "November".center(width): "Novembre".center(width), "December".center(width): "Décembre".center(width),
            }

@register.filter(is_safe=True)
def is_numeric(value):
    return "{}".format(value).isdigit()


@register.filter(name='is_checkbox')
def is_checkbox(field):
  return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__

#def field_sansentete(field):
@register.filter(name='field_entete')
def field_entete(field):
    type= str(field.field.widget.__class__.__name__)
    return (type in Constantes.typesAvecEntete)

@register.filter(name='nbsp')
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))


@register.filter(name='translate_month')
def translate_month(yearname):
    try:
        return Constantes.dicoMois[yearname]
    except:
        return yearname

@register.filter(name='translateOuiNon')
def translateOuiNon(truefalse):
    return "Oui" if truefalse else "Non"


@register.filter(is_safe=True)
def ordreTriStr(value):
    if value == '-date_creation':
        return "Date de création"
    elif value =='-date_dernierMessage':
        return "Date du dernier message"
    elif value =='-date_modification':
        return "Date de modification"
    elif value =='categorie':
        return "Catégorie"
    elif value =='titre':
        return "Titre"
    else:
        return value


@register.filter(is_safe=True)
def couperTexte(value, nb):
    if len(value) > nb:
        return value[:nb-3] + "..."
    return value


@register.filter(is_safe=True)
def adherent_asso(user, asso):
    return asso.is_membre(user)

@register.filter(is_safe=True)
def slug(txt):
    return slugify(txt)

@register.filter(is_safe=True)
def filtrerSuivis(nomSuivis):
    return Choix.nomSuivis[str(nomSuivis)]

@register.filter(is_safe=True)
def filtrerSuivisAgora(nomSuivis):
    try:
        if "agora" in str(nomSuivis):
            nomAsso = str(nomSuivis).split("_",1)[1]
            asso = Asso.objects.get(abreviation=nomAsso)
            return "Agora " + asso.nom
        else:
            nomSalon = str(nomSuivis).split("_",1)
            return "Salon " + nomSalon[1]
    except:
        return str(nomSuivis)


@register.filter(is_safe=True)
def filtrerSuivisForum(nomSuivis):
    try:
        nomAsso = str(nomSuivis).split("_",1)[1]
        asso = Asso.objects.get(abreviation=nomAsso)
        return "Articles " + asso.nom
    except:
        return str(nomSuivis)

@register.filter(is_safe=True)
def filtrerNotifSalon(nomSuivis):
    #return nomSuivis
    return str(nomSuivis).split(" (>")[0]

@register.filter(is_safe=True)
def distance(user1, user2):
    dist = None
    try:
        dist = user1.getDistance(user2)
    except:
        pass
    if dist == 0:
        return "-"
    elif dist == None:
        return "-"

    if dist < 10:
        if dist < 1:
            return "01 km"
        dist_int = int(dist + 0.5)
        if dist_int < 10:
            return "0" + str(int(dist + 0.5)) + " km"

    return str(int(dist + 0.5)) + " km"

@register.filter
def get_item_dict(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def random_name(longueur=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(longueur))
