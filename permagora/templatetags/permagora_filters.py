from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe
from django import template
import re

register = template.Library()

typesAvecEntete = ['Select', " NumberInput", "DateInput", "SummernoteWidget" ]#'Textarea',

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
    return (type in typesAvecEntete)

@register.filter(name='nbsp')
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))

def find_url(string):
    # findall() has been used
    # with valid conditions for urls in string
    #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] | [! * \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+', string)
    urls = re.findall('https?://[^\s]+', string)
    #urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', string)
    return urls

@register.filter(is_safe=True)
def url(value):
    url = find_url(value)
    newvalue = value
    for url_string in url:
        newurlstring = "<a href='" +url_string+"'>"+url_string+"</a>"
        newvalue = newvalue.replace(url_string, newurlstring)
    return newvalue