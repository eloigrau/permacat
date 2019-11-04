from django import template
import re

register = template.Library()

@register.filter(is_safe=True)
def difficulte(value):
    newvalue = str(value) +"fiiltee"
    return newvalue

@register.filter(is_safe=True)
def age(value):
    newvalue = str(value) +"agee"
    return newvalue

@register.filter(is_safe=True)
def temps(value):
    newvalue = str(value) +"tempse"
    return newvalue

@register.filter(is_safe=True)
def budget(value):
    newvalue = str(value) +"budgete"
    return newvalue

