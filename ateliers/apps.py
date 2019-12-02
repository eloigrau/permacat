from django.apps import AppConfig


class AteliersConfig(AppConfig):
    name = 'ateliers'
    #
    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('Article'))
    #     registry.register(self.get_model('Projet'))