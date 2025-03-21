from django.urls import path
from . import views

app_name = 'seo_analyzer'

urlpatterns = [
    path('dashboard/', views.SEODashboardView.as_view(), name='dashboard'),
    path('analyze/<int:content_id>/', views.analyze_seo, name='analyze'),
    path('analysis/<int:content_id>/', views.SEOAnalysisView.as_view(), name='analysis_detail'),
    path('analyze/run/', views.AnalyzeContentView.as_view(), name='run_analysis'),
] 