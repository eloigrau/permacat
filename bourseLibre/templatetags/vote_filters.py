from django import template
import re

register = template.Library()

@register.filter(is_safe=True)
def vote_statut(value):
    if value == '0':
        return "En cours"
    elif value =='1':
        return "Terminé"
    elif value =='2':
        return "Prévu"
    else:
        return value


@register.filter(is_safe=True)
def ordreTri(value):
    newvalue = value.replace('_', ' ').replace('-', '')
    return newvalue