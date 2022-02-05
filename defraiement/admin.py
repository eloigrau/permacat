from django.contrib import admin
from .models import Reunion, ParticipantReunion

# Register your models here.

admin.site.register(ParticipantReunion)
admin.site.register(Reunion)