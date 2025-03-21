from django.db import models
from django.conf import settings
from apps.content_manager.models import Content
from apps.accounts.models import CustomUser

class ContentAnalytics(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)
    avg_time_spent = models.IntegerField(default=0)  # saniye cinsinden
    bounce_rate = models.FloatField(default=0.0)  # yüzde cinsinden
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "İçerik Analitiği"
        verbose_name_plural = "İçerik Analitikleri"

    def __str__(self):
        return f"{self.content.title} Analitiği"

class DailyAnalytics(models.Model):
    date = models.DateField()
    total_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    avg_session_duration = models.IntegerField(default=0)  # saniye cinsinden
    bounce_rate = models.FloatField(default=0.0)  # yüzde cinsinden
    
    class Meta:
        verbose_name = "Günlük Analitik"
        verbose_name_plural = "Günlük Analitikler"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} Analitikleri"

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('view', 'Görüntüleme'),
        ('create', 'Oluşturma'),
        ('edit', 'Düzenleme'),
        ('delete', 'Silme'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kullanıcı Aktivitesi"
        verbose_name_plural = "Kullanıcı Aktiviteleri"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.content.title}"

class VisitorSession(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    user_agent = models.TextField()
    referrer = models.URLField(max_length=500, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=0)  # saniye cinsinden
    
    def __str__(self):
        return f"Session {self.session_id} for {self.content.title}"

class DailyMetrics(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    total_time_spent = models.PositiveIntegerField(default=0)  # saniye cinsinden
    
    class Meta:
        unique_together = ('content', 'date')
        verbose_name_plural = "Daily Metrics"
        
    def __str__(self):
        return f"Metrics for {self.content.title} on {self.date}" 