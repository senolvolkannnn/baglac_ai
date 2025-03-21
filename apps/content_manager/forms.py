from django import forms
from tinymce.widgets import TinyMCE
from .models import Content, Category

class ContentCreationForm(forms.ModelForm):
    CONTENT_TYPES = [
        ('blog', 'Blog Yazısı'),
        ('category', 'Kategori İçeriği'),
        ('product', 'Ürün İçeriği'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Taslak'),
        ('published', 'Yayınlandı'),
    ]

    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),
        required=False  # İçerik OpenAI tarafından oluşturulacak
    )
    
    content_type = forms.ChoiceField(
        label='İçerik Tipi',
        choices=CONTENT_TYPES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'
        })
    )

    status = forms.ChoiceField(
        label='Durum',
        choices=STATUS_CHOICES,
        initial='draft',
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'
        })
    )
    
    keywords = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
            'placeholder': 'Anahtar kelimeleri virgülle ayırarak yazın (max 200 karakter)'
        })
    )

    heading_structure = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Content
        fields = ['title', 'content', 'content_type', 'status', 'keywords', 'heading_structure']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6',
                'placeholder': 'İçerik başlığını girin'
            })
        }

    def clean(self):
        print("\n=== FORM TEMİZLEME BAŞLADI ===")
        cleaned_data = super().clean()
        print("Temizlenen veriler:", cleaned_data)
        print("POST verisi:", self.data)
        print("Dosyalar:", self.files if hasattr(self, 'files') else None)

        title = cleaned_data.get('title')
        keywords = cleaned_data.get('keywords')
        content_type = cleaned_data.get('content_type')
        heading_structure = cleaned_data.get('heading_structure')
        
        print(f"Başlık: {title}")
        print(f"Anahtar Kelimeler: {keywords}")
        print(f"İçerik Tipi: {content_type}")
        print(f"Başlık Yapısı: {heading_structure}")

        if not title:
            self.add_error('title', 'Başlık zorunludur.')
        elif len(title) < 5:
            self.add_error('title', 'Başlık en az 5 karakter olmalıdır.')

        if not keywords:
            self.add_error('keywords', 'Anahtar kelimeler zorunludur.')
        else:
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            if len(keyword_list) < 2:
                self.add_error('keywords', 'En az 2 anahtar kelime girilmelidir.')

        print("Form hataları:", self.errors if hasattr(self, 'errors') else None)
        print("=== FORM TEMİZLEME BİTTİ ===\n")
        
        return cleaned_data

class ContentGenerationForm(forms.Form):
    CONTENT_TYPES = [
        ('blog', 'Blog Yazısı'),
        ('category', 'Kategori İçeriği'),
        ('product', 'Ürün İçeriği'),
    ]

    title = forms.CharField(
        label='Ana Başlık',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    keywords = forms.CharField(
        label='Anahtar Kelimeler',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örnek: yapay zeka, makine öğrenmesi, derin öğrenme'
        })
    )

    tone = forms.ChoiceField(
        label='İçerik Tonu',
        choices=[
            ('professional', 'Profesyonel'),
            ('casual', 'Gündelik'),
            ('academic', 'Akademik'),
        ],
        widget=forms.RadioSelect
    )

    length = forms.ChoiceField(
        label='İçerik Uzunluğu',
        choices=[
            ('short', 'Kısa (~500 kelime)'),
            ('medium', 'Orta (~1000 kelime)'),
            ('long', 'Uzun (~2000 kelime)'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    content_type = forms.ChoiceField(
        label='Kategori',
        choices=CONTENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 