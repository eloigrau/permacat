from django import template
import re

register = template.Library()


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
        newurlstring = "<a href='" +url_string+"'" + " target='_blank'>"+url_string+"</a>"
        newvalue = newvalue.replace(url_string, newurlstring)
    return newvalue


@register.filter(is_safe=True)
def ordreTri(value):
    newvalue = value.replace('_', ' ').replace('-', '')
    return newvalue