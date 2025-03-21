from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_public')
    list_filter = ('is_public',)
    search_fields = ('key', 'value') 