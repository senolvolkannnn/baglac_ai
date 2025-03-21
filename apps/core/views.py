from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import SystemSettings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_settings'] = SystemSettings.objects.filter(is_public=True)
        return context

def health_check(request):
    """
    Sistem sağlık kontrolü için endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'version': '1.0.0'
    })

def home(request):
    return render(request, 'core/home.html') 