from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'
    #
    # def ready(self):
    #     from actstream import registry
    #     registry.register(self.get_model('Article'))
    #     registry.register(self.get_model('Projet'))