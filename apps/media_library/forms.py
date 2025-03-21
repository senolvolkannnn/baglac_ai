from django import forms
from .models import MediaFile

class MediaFileUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['title', 'description', 'file', 'file_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('Dosya boyutu 10MB\'ı geçemez.')
        return file 