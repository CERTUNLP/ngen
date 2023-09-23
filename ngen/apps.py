from django.apps import AppConfig


class NgenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ngen'

    def ready(self):
        import ngen.signals
