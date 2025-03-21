from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser
from django.conf import settings
from django.utils.text import slugify
import uuid

class Category(models.Model):
    BLOG = 'blog'
    CATEGORY = 'category'
    PRODUCT = 'product'
    
    CATEGORY_TYPES = [
        (BLOG, 'Blog'),
        (CATEGORY, 'Kategori İçeriği'),
        (PRODUCT, 'Ürün İçeriği'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES,
        default=BLOG
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Content(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Taslak'),
        ('published', 'Yayınlandı'),
        ('archived', 'Arşivlendi'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # SEO fields
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    
    # İçerik yapısı
    heading_structure = models.TextField(blank=True, null=True, help_text="JSON formatında başlık yapısı")
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def get_formatted_content(self):
        """İçeriği başlık ve paragraf bölümlerine ayırır"""
        sections = []
        lines = self.content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('**') and line.endswith('**'):
                # Başlık
                sections.append({
                    'type': 'heading',
                    'text': line.strip('*')
                })
            else:
                # Normal paragraf
                sections.append({
                    'type': 'paragraph',
                    'text': line
                })
        
        return sections

class ContentVersion(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    version_number = models.IntegerField()
    content_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('content', 'version_number')
        
    def __str__(self):
        return f"{self.content.title} - Version {self.version_number}" 