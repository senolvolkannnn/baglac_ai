from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomUserChangeForm, ProfileEditForm
from .models import UserProfile, CustomUser

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        try:
            response = super().form_valid(form)
            print("Login successful")  # Debug için
            return response
        except Exception as e:
            print(f"Login error: {str(e)}")  # Debug için
            raise

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['total_content'] = user.content_set.count()
        context['total_media'] = user.mediafile_set.count()
        context['recent_activities'] = user.useractivity_set.all()[:5]
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

class UserSettingsView(LoginRequiredMixin, UpdateView):
    form_class = CustomUserChangeForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')

    def get_object(self):
        return self.request.user 