from django.apps import AppConfig
import os

class MediaLibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.media_library'
    path = os.path.dirname(os.path.abspath(__file__)) 