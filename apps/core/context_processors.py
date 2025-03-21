from django.conf import settings
from .models import SystemSettings

def global_settings(request):
    """
    Tüm şablonlarda kullanılabilecek global ayarları sağlar
    """
    return {
        'DEBUG': settings.DEBUG,
        'SITE_NAME': 'AI Content Generator',
        'public_settings': SystemSettings.objects.filter(is_public=True),
    } 