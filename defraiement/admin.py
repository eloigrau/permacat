from django.contrib import admin
from .models import Reunion, ParticipantReunion, Distance_ParticipantReunion

# Register your models here.

admin.site.register(ParticipantReunion)
admin.site.register(Reunion)
admin.site.register(Distance_ParticipantReunion)