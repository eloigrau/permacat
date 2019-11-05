from django import template
from ..models import Choix
import re

register = template.Library()

@register.filter(is_safe=True)
def difficulte(value):
    return Choix.get_difficulte(value)

@register.filter(is_safe=True)
def age(value):
    return Choix.get_age(value)

@register.filter(is_safe=True)
def temps(value):
    return "<p> " + "{% fontawesome_icon 'clock' %} ".join([" " for i in range(int(value))]) + "</p>"

@register.filter(is_safe=True)
def budget(value):
    return "<p> " + "{% fontawesome_icon 'euro-sign' %} ".join([" " for i in range(int(value))]) + "</p>"


@register.filter(is_safe=True)
def categorie(value):
    return Choix.get_categorie(value)

