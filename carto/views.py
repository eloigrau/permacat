# carto/views.py

from datetime import datetime,  timedelta
from django.utils.safestring import mark_safe

from django.shortcuts import render
import simplejson
import requests

def carte(request):
    url = "https://presdecheznous.gogocarto.fr/api/elements.json?limit=500&bounds=1.75232%2C42.31794%2C3.24646%2C42.94034"

    reponse = requests.get(url)
    data = simplejson.loads(reponse.text)
    ev = data["data"]

    return render(request, 'carte.html', {'data':ev, 'titre': "La carte des colibris dans la région (presdecheznous.fr)" } )
