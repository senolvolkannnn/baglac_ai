from django.utils import timezone
from .models import ContentAnalytics, VisitorSession, DailyMetrics
from apps.content_manager.models import Content

class AnalyticsService:
    def track_view(self, content_id, session_id, ip_address, user=None, user_agent='', referrer=None):
        content = Content.objects.get(id=content_id)
        
        # Ziyaretçi oturumu oluştur
        session = VisitorSession.objects.create(
            content=content,
            session_id=session_id,
            ip_address=ip_address,
            user=user,
            user_agent=user_agent,
            referrer=referrer
        )
        
        # İçerik analitiğini güncelle
        analytics, created = ContentAnalytics.objects.get_or_create(content=content)
        analytics.views += 1
        analytics.save()
        
        # Günlük metrikleri güncelle
        today = timezone.now().date()
        daily_metrics, created = DailyMetrics.objects.get_or_create(
            content=content,
            date=today,
            defaults={
                'views': 1,
                'unique_visitors': 1
            }
        )
        if not created:
            daily_metrics.views += 1
            daily_metrics.save()
        
        return session 