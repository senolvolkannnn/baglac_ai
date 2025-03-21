from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import ContentAnalytics, DailyAnalytics, UserActivity
from apps.content_manager.models import Content
from apps.media_library.models import MediaFile
from apps.seo_analyzer.models import SEOAnalysis

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Temel istatistikler
        context['total_content'] = Content.objects.filter(author=user).count()
        context['total_media'] = MediaFile.objects.filter(uploader=user).count()
        
        # SEO analiz ortalaması
        seo_avg = SEOAnalysis.objects.filter(
            content__author=user
        ).aggregate(Avg('score'))['score__avg']
        context['avg_seo_score'] = round(seo_avg) if seo_avg else 0

        # Son 7 günlük içerik üretim trendi
        last_week = timezone.now() - timedelta(days=7)
        daily_content = Content.objects.filter(
            author=user,
            created_at__gte=last_week
        ).extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        context['dates'] = [d['date'].strftime('%d.%m') for d in daily_content]
        context['content_counts'] = [d['count'] for d in daily_content]

        # Son içerikler
        context['recent_contents'] = Content.objects.filter(
            author=user
        ).order_by('-created_at')[:5]

        return context

def track_view(request):
    if request.method == 'POST' and request.is_ajax():
        content_id = request.POST.get('content_id')
        service = AnalyticsService()
        service.track_view(
            content_id=content_id,
            session_id=request.session.session_key,
            ip_address=request.META.get('REMOTE_ADDR'),
            user=request.user if request.user.is_authenticated else None,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            referrer=request.META.get('HTTP_REFERER')
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}) 