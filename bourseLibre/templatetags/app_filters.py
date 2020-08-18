from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe

register = template.Library()

class Constantes:
    typesAvecEntete = ['Select', " NumberInput", "DateInput","DateTimeInputWidget", "SummernoteWidget" ]#'Textarea',
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
    elif value =='-type_vote':
        return "Type de vote"
    else:
        return value
