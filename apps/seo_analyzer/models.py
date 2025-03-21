from django.db import models
from django.conf import settings
from apps.content_manager.models import Content

class SEOAnalysis(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    title_score = models.IntegerField(default=0)
    description_score = models.IntegerField(default=0)
    keyword_score = models.IntegerField(default=0)
    overall_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "SEO Analizi"
        verbose_name_plural = "SEO Analizleri"

    def __str__(self):
        return f"{self.content.title} - {self.created_at}"

class KeywordAnalysis(models.Model):
    analysis = models.ForeignKey(SEOAnalysis, on_delete=models.CASCADE, null=True)
    keyword = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    density = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anahtar Kelime Analizi"
        verbose_name_plural = "Anahtar Kelime Analizleri"

    def __str__(self):
        return f"{self.keyword} - {self.density:.1f}%" 