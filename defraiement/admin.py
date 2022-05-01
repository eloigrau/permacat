from django.contrib import admin
from .models import Reunion, ParticipantReunion, Distance_ParticipantReunion

# Register your models here.

admin.site.register(ParticipantReunion)
admin.site.register(Reunion)
class Distance_ParticipantReunion_admin(admin.ModelAdmin):
    list_display = ('reunion', 'participant', 'distance')
admin.site.register(Distance_ParticipantReunion, Distance_ParticipantReunion_admin)