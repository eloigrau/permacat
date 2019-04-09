from django import template
from django.forms import CheckboxInput

register = template.Library()

typesSansEntete = ['TinyMCE' , 'Textarea', 'URLInput', 'EmailInput' ]

@register.filter(is_safe=True)
def is_numeric(value):
    return "{}".format(value).isdigit()


@register.filter(name='is_checkbox')
def is_checkbox(field):
  return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__

@register.filter(name='field_entete')
def field_entete(field):
    return field.field.widget.__class__.__name__ not in typesSansEntete