# -*- coding: utf-8 -*-
'''
Created on 25 mai 2017

@author: tchenrezi
'''
import itertools

from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponseForbidden

from .models import Profil
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from actstream.models import actor_stream


def handler404(request, *args, **kwargs):  #page not found
    response = render(request, "404.html")
    response.status_code = 404
    return response

def handler500(request, *args, **kwargs):   #erreur du serveur
    response = render(request, "500.html")
    response.status_code = 500
    return response

def handler403(request, *args, **kwargs):   #non autorisé
    response = render(request, "403.html")
    response.status_code = 403
    return response

def handler400(request, *args, **kwargs):   #requete invalide
    response = render(request, "400.html")
    response.status_code = 400
    return response



def presentation_site_pkoi(request):
    return render(request, 'asso/permacatpkoi.html')

def presentation_site_conseils(request):
    return render(request, 'conseilspratiques.html')

def presentation_site(request):
    return render(request, 'presentation_site.html')

def gallerie(request):
    return render(request, 'gallerie.html')

def faq(request):
    return render(request, 'faq.html')

def statuts(request):
    return render(request, 'asso/pc/statuts.html')

def statuts_rtg(request):
    return render(request, 'asso/rtg/statuts.html')

def statuts_fer(request):
    return render(request, 'statuts_fer.html')

@login_required
def profil_nom(request, user_username):
    try:
        user = Profil.objects.get(username=user_username)
        distance = user.getDistance(request.user)
        return render(request, 'profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
        return render(request, 'profil_inconnu.html', {'userid': user_username})

@login_required
def profil_inconnu(request):
    return render(request, 'profil_inconnu.html')


def charte(request):
    return render(request, 'asso/pc/charte.html', )

def cgu(request):
    return render(request, 'cgu.html', )

@login_required
def liens(request):
    liens = {"généraux" :[
        'https://grandjardin.jardiniersdunous.org /',
        'https://www.tizoom.fr',
        'https://transiscope.org',
        'https://www.mobicoop.fr/',
        'https://www.balotilo.org/',
        'https://colibris-universite.org/mooc-permaculture/wakka.php?wiki=PagePrincipale',
        'https://www.colibris-lemouvement.org/',
        'https://www.hameaux-legers.org/',
        'https://framasoft.org',
        'https://alternatiba.eu/alternatiba66/',
    ],
        "sites locaux " :[
        'https://tram66.org/',
        'http://terre-avenirs-peyrestortes.org/',
        'https://www.facebook.com/ramenetagraine/',
        'https://www.facebook.com/fermille/',
        'https://sel66.net',
        'https://ponteillanature.wixsite.com/eco-nature',
        'https://cce-66.wixsite.com/mysite',
        'https://jardindenat.wixsite.com/website',
        'https://www.permapat.com',
        'https://ecocharte.herokuapp.com',
        'https://pacteacvi.herokuapp.com',
        'https://www.tropique-du-papillon.com',
        'http://www.pepiniere-passiflore.com/'
        'http://lagalline.net',
        'https://val-respire.wixsite.com/asso',
        ],
        "à propos de la monnaie": [
        'https://www.monnaielibreoccitanie.org/',
        'http://lejeu.org/',
        'http://soudaqui.cat/wordpress/',
        ],
            "medias" : [
        #'https://agoratransition.herokuapp.com',
        'http://www.le-message.org/',
        'https://reporterre.net/',
        'https://la-bas.org/',
        'https://lvsl.fr/',
        'https://www.les-crises.fr/',
        ]
    }
    return render(request, 'liens.html', {'liens':liens})



def agenda(request):
    return render(request, 'agenda.html', )


@login_required
def activite(request, pseudo):
    profil = get_object_or_404(Profil, username=pseudo)
    stream = actor_stream(profil)

    return render(request, 'notifications/sesActions.html', {"pseudo":pseudo, "stream":stream})

class DeleteAccess:
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if hasattr(self.object, 'auteur'):
            if self.object.auteur == request.user or request.user.is_superuser:
                success_url = self.get_success_url()
                self.object.delete()
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer cet item")
        elif hasattr(self.object, 'user'):
            if self.object.user == request.user or request.user.is_superuser:
                success_url = self.get_success_url()
                self.object.delete()
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer cet item")
        else:
            if self.object == request.user or request.user.is_superuser:
                success_url = self.get_success_url()
                self.object.delete()
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer cet item")


