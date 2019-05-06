from django.apps import AppConfig

class BourseLibreConfig(AppConfig):
    name = 'bourseLibre'

    def ready(self):
        from actstream import registry
        from django.contrib.auth.models import Group
        from blog.models import Article, Projet
        registry.register(self.get_model('Profil'))
        registry.register(self.get_model('MessageGeneral'))
        registry.register(self.get_model('MessageGeneralPermacat'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Conversation'))
        registry.register(self.get_model('Produit'))
        registry.register(self.get_model('Produit_vegetal'))
        registry.register(self.get_model('Produit_service'))
        registry.register(self.get_model('Produit_objet'))
        registry.register(self.get_model('Produit_aliment'))
        registry.register(Article)
        registry.register(Projet)
        registry.register(Group)
