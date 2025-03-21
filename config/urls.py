from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),  # Ana sayfa için
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('content/', include('apps.content_manager.urls', namespace='content_manager')),
    path('seo/', include('apps.seo_analyzer.urls', namespace='seo')),
    path('media/', include('apps.media_library.urls', namespace='media')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('tinymce/', include('tinymce.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 