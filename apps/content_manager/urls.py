from django.urls import path
from . import views

app_name = 'content_manager'

urlpatterns = [
    # İçerik yönetimi URL'leri
    path('', views.ContentListView.as_view(), name='content_list'),  # Ana sayfa olarak içerik listesi
    path('create/', views.ContentCreateView.as_view(), name='content_create'),
    path('content/<slug:slug>/', views.ContentDetailView.as_view(), name='content_detail'),
    path('content/<slug:slug>/edit/', views.ContentUpdateView.as_view(), name='content_edit'),
    path('content/<slug:slug>/change-status/', views.change_content_status, name='change_status'),
    path('generate/', views.GenerateContentView.as_view(), name='generate_content'),
    
    # Anahtar Kelime Analizi URL'leri
    path('keywords/', views.KeywordAnalysisView.as_view(), name='keyword_analysis'),
    path('keywords/analyze/', views.KeywordAnalysisView.as_view(), name='analyze_keyword'),
    path('keywords/competitors/', views.CompetitorAnalysisView.as_view(), name='analyze_competitors'),
    path('keywords/brief/', views.ContentBriefView.as_view(), name='generate_brief'),
    
] 