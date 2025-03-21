from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import MediaFile
from .forms import MediaFileUploadForm

class MediaListView(LoginRequiredMixin, ListView):
    model = MediaFile
    template_name = 'media_library/media_list.html'
    context_object_name = 'media_files'
    paginate_by = 12

    def get_queryset(self):
        queryset = MediaFile.objects.filter(uploader=self.request.user)
        file_type = self.request.GET.get('type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_types'] = MediaFile.FILE_TYPES
        return context

class MediaUploadView(LoginRequiredMixin, CreateView):
    model = MediaFile
    form_class = MediaFileUploadForm
    template_name = 'media_library/media_upload.html'
    success_url = reverse_lazy('media_library:media_list')

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)

class MediaDetailView(LoginRequiredMixin, DetailView):
    model = MediaFile
    template_name = 'media_library/media_detail.html'
    context_object_name = 'media'

    def get_queryset(self):
        return MediaFile.objects.filter(uploader=self.request.user)

class MediaDeleteView(LoginRequiredMixin, DeleteView):
    model = MediaFile
    success_url = reverse_lazy('media_library:media_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.uploader == request.user:
            self.object.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Permission denied'}) 