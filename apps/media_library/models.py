from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser
from django.conf import settings
from django.utils.text import slugify
import os

class MediaCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Media Categories"
        
    def __str__(self):
        return self.name

def upload_to(instance, filename):
    """Dosya yükleme yolunu belirler"""
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}.{ext}"
    return os.path.join('media_files', instance.file_type, filename)

class MediaFile(models.Model):
    FILE_TYPES = (
        ('image', 'Görsel'),
        ('video', 'Video'),
        ('document', 'Doküman'),
        ('other', 'Diğer'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_to)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    file_size = models.IntegerField(editable=False)  # bytes cinsinden
    mime_type = models.CharField(max_length=100, editable=False)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medya Dosyası"
        verbose_name_plural = "Medya Dosyaları"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.mime_type = self.file.content_type
        super().save(*args, **kwargs)

    @property
    def file_size_display(self):
        """Dosya boyutunu okunabilir formatta döndürür"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def is_image(self):
        return self.file_type == 'image'

    @property
    def is_video(self):
        return self.file_type == 'video'

    @property
    def thumbnail_url(self):
        if self.is_image:
            return self.file.url
        # Diğer dosya tipleri için varsayılan ikonlar
        return {
            'video': '/static/images/video-thumbnail.png',
            'document': '/static/images/document-thumbnail.png',
            'other': '/static/images/file-thumbnail.png',
        }.get(self.file_type, '/static/images/file-thumbnail.png')

class MediaUsage(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=100)  # Hangi model içinde kullanıldığı
    object_id = models.PositiveIntegerField()  # İlgili model instance'ının ID'si
    used_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.media_file.title} used in {self.content_type}" 