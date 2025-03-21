from django.contrib import admin
from .models import MediaFile, MediaCategory, MediaUsage

@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'uploader', 'file_size_display', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['file_size', 'mime_type', 'created_at', 'updated_at']

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'description', 'file', 'file_type')
        }),
        ('Dosya Bilgileri', {
            'fields': ('file_size', 'mime_type'),
            'classes': ('collapse',)
        }),
        ('Diğer Bilgiler', {
            'fields': ('uploader', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Yeni dosya yükleniyorsa
            obj.uploader = request.user
        super().save_model(request, obj, form, change)

@admin.register(MediaUsage)
class MediaUsageAdmin(admin.ModelAdmin):
    list_display = ['media_file', 'content_type', 'object_id', 'used_at']
    list_filter = ['content_type', 'used_at']
    search_fields = ['media_file__title']
    readonly_fields = ['used_at'] 