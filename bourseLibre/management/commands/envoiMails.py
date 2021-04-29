from django.core.management.base import BaseCommand
from bourseLibre.views_admin import envoyerEmails

class Command(BaseCommand):
    help = "Envoi des mails d'alerte"

    def handle(self, *args, **options):
        envoyerEmails()