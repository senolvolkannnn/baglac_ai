from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import SEOAnalysis, KeywordAnalysis
from apps.content_manager.models import Content
from .services import SEOAnalyzer
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

class SEODashboardView(LoginRequiredMixin, ListView):
    model = SEOAnalysis
    template_name = 'seo_analyzer/dashboard.html'
    context_object_name = 'analyses'
    
    def get_queryset(self):
        return SEOAnalysis.objects.filter(
            content__author=self.request.user
        ).select_related('content')

class SEOAnalysisView(LoginRequiredMixin, DetailView):
    model = SEOAnalysis
    template_name = 'seo_analyzer/analysis_detail.html'
    context_object_name = 'analysis'
    
    def get_object(self):
        content_id = self.kwargs.get('content_id')
        content = get_object_or_404(Content, id=content_id, author=self.request.user)
        analysis, created = SEOAnalysis.objects.get_or_create(content=content)
        return analysis

class AnalyzeContentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        content_id = request.POST.get('content_id')
        content = get_object_or_404(Content, id=content_id, author=request.user)
        
        analyzer = SEOAnalyzer(content)
        analysis_result = analyzer.analyze()
        analysis = analyzer.save_analysis()
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse_lazy('seo_analyzer:analysis_detail', kwargs={'content_id': content.id})
        })

class SEOAnalyzerView(View):
    template_name = 'seo_analyzer/analyzer.html'

    def get(self, request):
        contents = Content.objects.filter(author=request.user)
        return render(request, self.template_name, {'contents': contents})

    def post(self, request):
        content_id = request.POST.get('content_id')
        content = Content.objects.get(id=content_id)
        
        # SEO analizi yap
        analysis_result = self.analyze_content(content)
        
        return render(request, self.template_name, {
            'content': content,
            'analysis': analysis_result
        })

    def analyze_content(self, content):
        # SEO analiz mantığı burada
        return {
            'title_length': len(content.seo_title),
            'description_length': len(content.seo_description),
            'keyword_density': self.calculate_keyword_density(content),
            # diğer metrikler...
        }

@login_required
@require_http_methods(["POST"])
def analyze_seo(request, content_id):
    content = Content.objects.get(id=content_id, author=request.user)
    
    # SEO analizi yap
    title_length = len(content.seo_title)
    description_length = len(content.seo_description)
    
    # Başlık analizi
    title_score = 100
    if title_length < 30:
        title_score -= 30
    elif title_length > 60:
        title_score -= 20
        
    # Açıklama analizi
    description_score = 100
    if description_length < 120:
        description_score -= 30
    elif description_length > 160:
        description_score -= 20
        
    # Anahtar kelime analizi
    keywords = content.keywords.split(',')
    keyword_density = len(keywords) / len(content.content.split()) * 100
    keyword_score = 100
    if keyword_density < 1:
        keyword_score -= 30
    elif keyword_density > 3:
        keyword_score -= 20
    
    # Genel skor
    overall_score = round((title_score + description_score + keyword_score) / 3)
    
    # Analizi kaydet
    SEOAnalysis.objects.create(
        content=content,
        title_score=title_score,
        description_score=description_score,
        keyword_score=keyword_score,
        overall_score=overall_score
    )
    
    return JsonResponse({
        'title_length': title_length,
        'title_score': title_score,
        'description_length': description_length,
        'description_score': description_score,
        'keyword_density': round(keyword_density, 2),
        'keyword_score': keyword_score,
        'overall_score': overall_score
    }) 