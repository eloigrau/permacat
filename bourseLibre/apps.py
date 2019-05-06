from django.apps import AppConfig

class BourseLibreConfig(AppConfig):
    name = 'bourseLibre'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Profil'))
        registry.register(self.get_model('MessageGeneral'))
        registry.register(self.get_model('MessageGeneralPermacat'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Conversation'))
        registry.register(self.get_model('Produit'))


