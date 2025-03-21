from django.apps import AppConfig
import os

class SeoAnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.seo_analyzer'
    path = os.path.dirname(os.path.abspath(__file__)) 