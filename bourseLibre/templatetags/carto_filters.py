from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def to_numeric(value):
    return str(value).replace(',', '.')


@register.filter(is_safe=True)
def texte(value):
    return mark_safe(str(value).replace('\'', '_').replace('\"', '_'))