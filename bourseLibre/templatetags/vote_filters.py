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



@register.filter
def candidate(candidate, candidates):
    """Get a candidate from the dict."""
    return candidates[candidate]

@register.filter
def getVoteStr_questionB(vote, question):
    return vote.getVoteStr_questionB(question)

@register.filter
def getVoteStr_proposition_m(vote, proposition):
    return vote.getVoteStr_proposition_m(proposition)
