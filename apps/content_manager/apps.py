from django.apps import AppConfig
import os

class ContentManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.content_manager'
    path = os.path.dirname(os.path.abspath(__file__))

    def ready(self):
        try:
            import apps.content_manager.signals
        except ImportError:
            pass 