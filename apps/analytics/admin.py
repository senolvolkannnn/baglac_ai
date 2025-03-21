from django.contrib import admin
from .models import ContentAnalytics, DailyAnalytics, UserActivity, VisitorSession, DailyMetrics

@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['content', 'view_count', 'avg_time_spent', 'bounce_rate', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content__title']
    readonly_fields = ['view_count', 'avg_time_spent', 'bounce_rate', 'created_at', 'updated_at']

@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_views', 'unique_visitors', 'avg_session_duration', 'bounce_rate']
    list_filter = ['date']
    readonly_fields = ['total_views', 'unique_visitors', 'avg_session_duration', 'bounce_rate']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'activity_type', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'content__title']
    readonly_fields = ['created_at']

@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ['content', 'session_id', 'ip_address', 'start_time', 'duration']
    list_filter = ['start_time']
    search_fields = ['content__title', 'session_id', 'ip_address']
    readonly_fields = ['start_time', 'end_time', 'duration']

@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ['content', 'date', 'views', 'unique_visitors', 'total_time_spent']
    list_filter = ['date']
    search_fields = ['content__title']
    readonly_fields = ['views', 'unique_visitors', 'total_time_spent'] 