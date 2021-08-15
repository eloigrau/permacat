"""Templatetags for django-jugemaj."""
from django import template

register = template.Library()


@register.filter
def candidate(candidate, candidates):
    """Get a candidate from the dict."""
    return candidates[candidate]
