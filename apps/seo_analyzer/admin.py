from django.contrib import admin
from .models import SEOAnalysis, KeywordAnalysis

@admin.register(SEOAnalysis)
class SEOAnalysisAdmin(admin.ModelAdmin):
    list_display = ['content', 'overall_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content__title']
    readonly_fields = ['title_score', 'description_score', 'keyword_score', 'overall_score', 'created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content')

@admin.register(KeywordAnalysis)
class KeywordAnalysisAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'count', 'density', 'created_at']
    list_filter = ['created_at']
    search_fields = ['keyword']
    readonly_fields = ['count', 'density', 'created_at'] 