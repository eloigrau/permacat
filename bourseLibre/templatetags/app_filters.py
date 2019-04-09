from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe

register = template.Library()

typesAvecEntete = ['Textarea', 'Select', " NumberInput", "DateInput", "SummernoteWidget" ]

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
def field_sansentete(field):
    type= str(field.field.widget.__class__.__name__)
    return (type in typesAvecEntete)

@register.filter(name='nbsp')
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))