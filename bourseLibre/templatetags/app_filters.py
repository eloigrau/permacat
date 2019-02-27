from django import template

register = template.Library()


@register.filter(is_safe=True)
def is_numeric(value):
    return "{}".format(value).isdigit()
