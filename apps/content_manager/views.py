from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from anthropic import Anthropic
import time
from .models import Content, Category
from .forms import ContentCreationForm, ContentGenerationForm
import logging
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
import re
from .utils.semrush import SEMrushAPI
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from typing import List, Dict
from urllib.parse import urlparse
import httpx
import asyncio
from django.http import StreamingHttpResponse
from asgiref.sync import async_to_sync
import random

logger = logging.getLogger(__name__)

# İçerik tipi belirleme fonksiyonu
def determine_content_type(title, subtitles):
    """İçerik tipini belirle"""
    return 'genel'

# Format talimatları fonksiyonu
def get_format_instructions(content_type, tone):
    """İçerik tipine göre format talimatları döndür"""
    format_instructions = {
        'blog': """
        FORMAT: Blog yazısı formatı
        ZORUNLU YAPI:
        • Alt başlıklar ile bölümlendirilmiş içerik
        • Her bölümde detaylı açıklamalar
        • Maddeleme olan yerlerde, maddeleri sırasıyla ver ve sonrasında o maddeleri paragraf olarak açıkla.
        • Konu ile ilgili sıkça sorulan sorular ekle.
        """,
        
        'category': """
        FORMAT: Kategori sayfası formatı
        ZORUNLU YAPI:
        • Kategori genel tanıtımı
        • Öne çıkan ürün/hizmet grupları
        • Kategori avantajları
        • Seçim kriterleri
        """,
        
        'product': """
        FORMAT: Ürün içeriği formatı
        ZORUNLU YAPI:
        • Ürün tanıtımı ve özellikleri
        • Teknik detaylar
        • Kullanım alanları
        • Avantajlar ve faydalar
        • Satın alma rehberi
        """,
    }
    
    # Ton seçimine göre dil ayarları
    tone_instructions = {
        'professional': """
        DİL TARZI:
        • Resmi ve profesyonel ton
        • Teknik terimler kullanımı
        • Kanıtlanabilir veriler
        • Uzman bakış açısı
        """,
        
        'casual': """
        DİL TARZI:
        • Gündelik ve samimi ton
        • Anlaşılır dil kullanımı
        • Pratik örnekler
        • Sohbet tarzı anlatım
        """,
        
        'academic': """
        DİL TARZI:
        • Akademik ve formal ton
        • Bilimsel terminoloji
        • Araştırma verileri
        • Kaynak gösterimi
        """
    }

    base_instructions = format_instructions.get(content_type, format_instructions['blog'])
    tone_instruction = tone_instructions.get(tone, tone_instructions['professional'])
    
    return f"{base_instructions}\n\n{tone_instruction}"

class ContentListView(LoginRequiredMixin, ListView):
    model = Content
    template_name = 'content_manager/content_list.html'
    context_object_name = 'contents'

    def get_queryset(self):
        return Content.objects.filter(author=self.request.user)

class ContentDetailView(LoginRequiredMixin, DetailView):
    model = Content
    template_name = 'content_manager/content_detail.html'

    def get_queryset(self):
        return Content.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formatted_content = self.format_content(self.object.content)
        context['formatted_content'] = mark_safe(formatted_content)
        return context

    def format_content(self, content):
        lines = content.split('\n')
        formatted_lines = []

        for line in lines:
            # Markdown bold (**) formatını HTML'e çevir
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)

            # Ana başlıklar için (H2)
            if line.startswith('##'):
                clean_title = line.replace('##', '').strip()
                formatted_lines.append(f'<h2 class="text-2xl font-bold my-4">{clean_title}</h2>')
            elif line.startswith('#'):
                clean_title = line.replace('#', '').strip()
                formatted_lines.append(f'<h2 class="text-2xl font-bold my-4">{clean_title}</h2>')
            # Madde işaretli satırlar için
            elif line.strip().startswith('*'):
                clean_item = line.replace('*', '').strip()
                formatted_lines.append(f'<li class="flex items-center my-2"><span class="mr-2">•</span>{clean_item}</li>')
            # Normal paragraflar için
            elif line.strip():
                formatted_lines.append(f'<p class="my-4">{line}</p>')

        return '\n'.join(formatted_lines)

class ContentCreateView(LoginRequiredMixin, CreateView):
    model = Content
    template_name = 'content_manager/content_form.html'
    form_class = ContentCreationForm

    def form_valid(self, form):
        print("\n=== FORM VALID BAŞLADI ===")
        try:
            # Form verilerini al ve logla
            print("Form Data:", self.request.POST)
            print("Form Files:", self.request.FILES)
            print("Form Cleaned Data:", form.cleaned_data)

            # Formu kaydetmeden önce yazarı ata
            form.instance.author = self.request.user
            print("Yazar atandı:", self.request.user)

            # Başlık yapısını al
            heading_structure = self.request.POST.get('heading_structure', '[]')
            try:
                # JSON olarak parse etmeyi dene
                import json
                json.loads(heading_structure)
                print("Başlık yapısı (POST'tan):", heading_structure)
            except Exception as e:
                print("Başlık yapısı JSON parse hatası:", str(e))
                heading_structure = '[]'
            
            # Başlık yapısını form instance'a ekle
            form.instance.heading_structure = heading_structure

            # İçerik tipini belirle
            content_type = form.cleaned_data.get('content_type', 'blog')
            print("İçerik tipi:", content_type)

            # İçerik uzunluğunu belirle
            content_length = self.request.POST.get('length', 'medium')
            word_count = 1000  # Varsayılan (orta)
            if content_length == 'short':
                word_count = 500
            elif content_length == 'long':
                word_count = 2000
            print("İçerik uzunluğu:", word_count)

            # İçerik tonunu al
            tone = self.request.POST.get('tone', 'professional')

            # Claude ile içerik oluştur
            content = self.generate_content_with_assistant(
                title=form.cleaned_data['title'],
                heading_structure=heading_structure,
                keywords=form.cleaned_data['keywords'],
                tone=tone,
                length=word_count,
                content_type=content_type
            )
            
            if not content:
                error_message = "Claude şu anda çok yoğun ve içerik oluşturulamadı. Lütfen biraz sonra tekrar deneyin."
                messages.error(self.request, error_message)
                
                # Form instance'ını içerik olmadan kaydet (draft olarak)
                form.instance.content = "[Otomatik içerik oluşturulamadı. Manuel olarak düzenleyebilirsiniz]"
                
                # Formu kaydet
                self.object = form.save()
                
                # Hata ile birlikte detay sayfasına yönlendir
                return HttpResponseRedirect(self.get_success_url())
            
            # İçeriği form instance'a ekle
            form.instance.content = content
            
            # SEO içeriği oluştur
            try:
                seo_content = self.generate_seo_content(
                    title=form.cleaned_data['title'],
                    keywords=form.cleaned_data['keywords']
                )
                
                if seo_content and 'title' in seo_content and 'description' in seo_content:
                    form.instance.seo_title = seo_content['title']
                    form.instance.seo_description = seo_content['description']
            except Exception as e:
                print(f"SEO içerik oluşturma hatası: {str(e)}")
                # SEO içeriği oluşturulmazsa devam et
            
            # Progress durumunu güncelle
            self.send_progress_update("content_saved", "İçerik kaydedildi!")
            
            # Formu kaydet
            return super().form_valid(form)
            
        except Exception as e:
            print(f"\nFORM VALID HATASI: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f"Bir hata oluştu: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("\n=== FORM GEÇERSİZ ===")
        print("Form hataları:", form.errors)
        print("Form alanları:", form.fields)
        print("POST verisi:", self.request.POST)
        print("FILES verisi:", self.request.FILES)
        print("Form temizlenmiş veriler:", form.cleaned_data if hasattr(form, 'cleaned_data') else None)
        
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        
        error_str = ", ".join(error_messages) if error_messages else "Bilinmeyen form hatası"
        messages.error(self.request, f"Form hataları: {error_str}")
        
        print("=== FORM GEÇERSİZ SONU ===\n")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('content_manager:content_detail', kwargs={'slug': self.object.slug})

    def generate_content_with_assistant(self, title, heading_structure, keywords, tone, length, content_type):
        """Claude-3.7 Sonnet ile içerik üretimi"""
        try:
            # Progress durumunu başlat
            self.send_progress_update("draft_started", "Claude-3.7 Sonnet ile içerik oluşturuluyor...")
            logger.info("Claude-3.7 Sonnet ile içerik üretimi başlıyor")
            
            content = self._generate_draft_with_claude(title, heading_structure, keywords, tone, length, content_type)
            if not content:
                logger.error("Claude-3.7 Sonnet içerik üretimi başarısız")
                return None

            # Progress durumunu güncelle
            self.send_progress_update("content_completed", "İçerik başarıyla oluşturuldu!")
            logger.info("İçerik üretimi tamamlandı")
            
            return content

        except Exception as e:
            logger.error(f"İçerik üretimi hatası: {str(e)}")
            return None

    def _generate_draft_with_claude(self, title, heading_structure, keywords, tone, length, content_type):
        """Claude-3.7 Sonnet ile gelişmiş içerik oluşturma"""
        try:
            api_key = settings.ANTHROPIC_API_KEY.strip()
            if not api_key:
                logger.error("ANTHROPIC_API_KEY ayarlanmamış")
                return None

            # Hata türlerini doğru modülden import et
            try:
                from anthropic.types import RateLimitError, APIStatusError
            except ImportError:
                from anthropic import RateLimitError, APIStatusError
            
            # Yeniden deneme parametrelerini güncelle
            max_retries = 5  # Arttırıldı
            base_delay = 3   # Başlangıç bekleme süresi
            max_delay = 30   # Maksimum bekleme süresi
            current_retry = 0
            
            anthropic = Anthropic(
                api_key=api_key,
                timeout=600,
                max_retries=1
            )

            # Başlık yapısını JSON olarak parse et
            try:
                if isinstance(heading_structure, str):
                    import json
                    heading_structure_parsed = json.loads(heading_structure)
                else:
                    heading_structure_parsed = heading_structure
                
                # Başlık yapısını formatlı şekilde hazırla
                formatted_headings = []
                for section in heading_structure_parsed:
                    h2_title = section['h2']
                    formatted_headings.append(f"## {h2_title}")
                    
                    if section['h3s']:
                        for h3_title in section['h3s']:
                            formatted_headings.append(f"### {h3_title}")
                
                headings_text = "\n".join(formatted_headings)
            except Exception as e:
                logger.error(f"Başlık yapısı işlenirken hata: {str(e)}")
                headings_text = "## Oluşturucu Hatası\nBaşlık yapısı işlenemiyor"

            content_request = f"""Başlık: {title}

Başlık Yapısı:
{headings_text}

Anahtar Kelimeler: {keywords}
Kelime Sayısı: {length}
Ton: {tone}

YAZIM KILAVUZU:
1. İçerik Yaklaşımı:
   - Her bölüm kendi doğal akışında ilerlemeli
   - Format zorlaması olmadan, konunun gerektirdiği şekilde yazılmalı
   - Paragraflar akıcı ve bağlantılı olmalı

2. Alt Başlık Formatları:
   a) Numaralandırma Kullanılacak Başlıklar:
      - "Dikkat Edilmesi Gerekenler" içeren başlıklar
      - "Önemli Noktalar" içeren başlıklar
      - "Yapılması Gerekenler" içeren başlıklar
      - "Nasıl" ile başlayan başlıklar
      - "Yöntem" veya "Süreç" içeren başlıklar
      Bu başlıklarda:
      1. Her madde numaralandırılmalı
      2. Her madde 2-3 cümle ile açıklanmalı
      3. Maddeler arası geçiş cümleleri kullanılmalı

   b) Maddeleme Kullanılacak Başlıklar:
      - "Gerekli Belgeler" içeren başlıklar
      - "Şartlar" veya "Koşullar" içeren başlıklar
      - "Avantajlar" veya "Dezavantajlar" içeren başlıklar
      - "Faydalar" veya "Zararlar" içeren başlıklar
      Bu başlıklarda:
      • Maddeler noktalı liste şeklinde verilmeli
      • Her madde kısa ve öz olmalı
      • Gerekirse maddelerin altında kısa açıklamalar yapılmalı

   c) Paragraf Formatında Yazılacak Başlıklar:
      - "Nedir", "Ne Demek", "Tanım", "Hakkında" içeren başlıklar
      - Genel bilgi ve açıklama içeren diğer başlıklar
      Bu başlıklarda:
      - Akıcı ve bağlantılı paragraflar kullanılmalı
      - Teknik terimler açıklanmalı
      - Örneklerle zenginleştirilmeli

3. H3 Başlıklar için Özel Kurallar:
   - Her H3 başlığı kendi konusuna odaklanmalı
   - H2 başlığıyla uyumlu olmalı
   - Detaylı ve spesifik bilgiler içermeli
   - H2'nin alt başlığı olduğunu unutmadan bağlantılı yazılmalı

4. Genel Kurallar:
   - Her bölüm kendi içinde tutarlı olmalı
   - Başlığın yapısına göre uygun format seçilmeli
   - Gerektiğinde formatlar birleştirilebilir
   - Okuyucu için en anlaşılır format tercih edilmeli

Not: İçeriği [İÇERİK BAŞLANGIÇ] ve [İÇERİK BİTİŞ] etiketleri arasında yaz."""

            print("Claude-3.7 Sonnet içerik talebi hazırlandı")

            # Yeniden deneme mantığı
            while current_retry < max_retries:
                try:
                    print(f"Claude API isteği gönderiliyor (deneme {current_retry + 1}/{max_retries})...")
                    
                    # Her denemeden önce rastgele bekleme süresi ekle
                    if current_retry > 0:
                        wait_time = min(base_delay * (2 ** current_retry) + random.uniform(0, 2), max_delay)
                        print(f"Bekleme süresi: {wait_time:.1f} saniye...")
                        time.sleep(wait_time)
                    
                    response = anthropic.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=12000,
                        messages=[{
                            "role": "user",
                            "content": content_request
                        }],
                        temperature=0.7
                    )
                    
                    # Başarılı yanıt kontrolü
                    if response and hasattr(response, 'content') and response.content:
                        content = response.content[0].text
                        if content and len(content.split()) >= 50:
                            print("Claude API yanıtı başarılı!")
                            return content.replace("[İÇERİK BAŞLANGIÇ]", "").replace("[İÇERİK BİTİŞ]", "").strip()
                    
                    # Yanıt geçersizse tekrar dene
                    current_retry += 1
                    continue
                    
                except (RateLimitError, APIStatusError) as e:
                    current_retry += 1
                    error_code = getattr(e, 'status_code', None)
                    
                    if current_retry >= max_retries:
                        print(f"Son deneme başarısız. Hata: {str(e)}")
                        return None
                        
                    wait_time = min(base_delay * (2 ** current_retry) + random.uniform(0, 2), max_delay)
                    print(f"API hatası (kod: {error_code}), {wait_time:.1f} saniye bekleniyor...")
                    time.sleep(wait_time)
                
                except Exception as e:
                    error_str = str(e).lower()
                    if "529" in error_str or "overloaded" in error_str:
                        current_retry += 1
                        if current_retry >= max_retries:
                            print("Maksimum deneme sayısına ulaşıldı.")
                            return None
                            
                        wait_time = min(base_delay * (2 ** current_retry) + random.uniform(0, 2), max_delay)
                        print(f"Genel hata (aşırı yük), {wait_time:.1f} saniye bekleniyor...")
                        time.sleep(wait_time)
                    else:
                        print(f"Beklenmeyen hata: {str(e)}")
                        return None

            print("Tüm denemeler başarısız oldu.")
            return None

        except Exception as e:
            print(f"\nCLAUDE İÇERİK ÜRETİM HATASI: {str(e)}")
            return None

    def send_progress_update(self, stage, message):
        """Progress durumunu frontend'e gönder"""
        try:
            response = JsonResponse({
                'stage': stage,
                'message': message,
                'progress': 50 if stage == 'draft_started' else 75
            })
            response['X-Progress-Update'] = 'true'
            return response
        except Exception as e:
            logger.error(f"Progress güncelleme hatası: {str(e)}")

    def generate_seo_content(self, title, keywords):
        """SEO başlık ve açıklama oluştur"""
        return {
            'title': title,
            'description': ""
        }

class GenerateContentView(LoginRequiredMixin, CreateView):
    form_class = ContentGenerationForm
    template_name = 'content_manager/generate_content.html'
    success_url = reverse_lazy('content_manager:content_list')

    def form_valid(self, form):
        try:
            # Form verilerini al
            title = form.cleaned_data['title']
            subtitles = self.request.POST.getlist('subtitles[]')
            keywords = form.cleaned_data['keywords']
            tone = self.request.POST.get('tone')
            length = self.request.POST.get('length')
            content_type = form.cleaned_data['content_type']

            # İçerik uzunluğunu belirle
            length_words = {
                'short': 500,
                'medium': 1000,
                'long': 2000
            }.get(length, 1000)

            # İçerik üretimi için Claude-3.7 Sonnet'i kullan
            generated_content = self.generate_content_with_assistant(
                title=title,
                subtitles=subtitles,
                keywords=keywords,
                tone=tone,
                length=length_words,
                content_type=content_type
            )

            # İçeriği göster
            return render(self.request, 'content_manager/generate_content.html', {
                'form': form,
                'generated_content': generated_content,
                'title': title,
                'keywords': keywords
            })

        except Exception as e:
            form.add_error(None, f"İçerik üretilirken bir hata oluştu: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

class ContentUpdateView(LoginRequiredMixin, UpdateView):
    model = Content
    template_name = 'content_manager/content_form.html'
    fields = ['title', 'content', 'category', 'seo_title', 'seo_description', 'keywords']

    def get_queryset(self):
        # Sadece kullanıcının kendi içeriklerini düzenleyebilmesi için
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('content_manager:content_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'İçerik Düzenle'
        context['button_text'] = 'Güncelle'
        return context

@login_required
def change_content_status(request, slug):
    content = get_object_or_404(Content, slug=slug, author=request.user)

    # Durumu değiştir
    if content.status == 'draft':
        content.status = 'published'
    elif content.status == 'published':
        content.status = 'draft'
    elif content.status == 'archived':
        content.status = 'draft'

    content.save()

    return JsonResponse({
        'success': True,
        'new_status': content.status,
        'status_display': content.get_status_display()
    })

@method_decorator(csrf_exempt, name='dispatch')
class KeywordAnalysisView(View):
    template_name = 'content_manager/keyword_analysis.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            data = json.loads(request.body)
            keyword = data.get('keyword')

            if not keyword:
                return JsonResponse({'error': 'Anahtar kelime gerekli'}, status=400)

            semrush = SEMrushAPI()

            # Ana anahtar kelime analizi
            analysis = semrush.analyze_keyword(keyword)

            # İlgili kelimeleri ve rakipleri al
            related_keywords = semrush.get_related_keywords(keyword)
            competitors = semrush.get_competitors(keyword)

            # Kelimeleri filtrele ve kategorize et
            categorized_keywords = self.filter_and_categorize_keywords(
                keywords=related_keywords,
                main_keyword=keyword,
                competitors=competitors
            )

            # API yanıtını oluştur
            response_data = {
                'keyword': keyword,
                'volume': analysis.get('volume', 0),
                'cpc': analysis.get('cpc', 0),
                'competition': analysis.get('competition', 0),
                'results': analysis.get('results', 0),
                'trend': analysis.get('trend', {}),
                'related_keywords': related_keywords[:10],  # İlk 10 ilgili kelime
                'competitors': competitors[:10],  # İlk 10 rakip
                'content_optimization': categorized_keywords  # Kategorize edilmiş kelimeler
            }

            return JsonResponse(response_data)

        except Exception as e:
            print(f"\nHATA: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def filter_and_categorize_keywords(self, keywords: List[Dict], main_keyword: str, competitors: List[Dict]) -> Dict:
        """
        Anahtar kelimeleri filtreler ve kategorize eder
        """
        # Rakip domainlerden marka isimlerini çıkar
        brand_hints = set()
        for comp in competitors:
            domain = comp['domain'].lower()
            domain = domain.replace('www.', '').split('.')[0]
            if domain not in ['amazon', 'trendyol', 'hepsiburada', 'n11', 'gittigidiyor']:
                brand_hints.add(domain)

        def is_likely_brand(keyword: str) -> bool:
            keyword = keyword.lower()
            if any(brand in keyword for brand in brand_hints):
                return True
            # Sadece sayı içeren kelimeleri filtrele
            if keyword.replace(' ', '').isdigit():
                return True
            return False

        def is_valid_keyword(kw: Dict) -> bool:
            keyword = kw['keyword'].lower()
            main_kw = main_keyword.lower()

            # Sadece ana kelimenin aynısını filtrele
            if keyword == main_kw:
                return False

            # Marka benzeri kelimeleri filtrele
            if is_likely_brand(keyword):
                return False

            return True

        # Kelimeleri filtrele ve kategorize et
        categories = {
            'primary_keywords': [],    # Yüksek hacimli ve alakalı
            'secondary_keywords': [],  # Orta hacimli ve alakalı
            'long_tail_keywords': []   # Düşük hacimli ama çok alakalı
        }

        # Önce tüm geçerli kelimeleri topla
        valid_keywords = [kw for kw in keywords if is_valid_keyword(kw)]

        # Hacme göre sırala
        valid_keywords.sort(key=lambda x: int(x.get('volume', 0)), reverse=True)

        # Hacim eşiklerini dinamik olarak belirle
        if valid_keywords:
            volumes = [int(kw.get('volume', 0)) for kw in valid_keywords]
            max_volume = max(volumes)
            high_threshold = max_volume * 0.3  # En yüksek hacmin %30'u
            med_threshold = max_volume * 0.1   # En yüksek hacmin %10'u
        else:
            high_threshold = 1000
            med_threshold = 300

        for kw in valid_keywords:
            relevance = float(kw.get('relevance', 0))
            volume = int(kw.get('volume', 0))
            word_count = len(kw['keyword'].split())

            # Long tail kelimeler (3+ kelime)
            if word_count >= 3:
                categories['long_tail_keywords'].append(kw)
                continue

            # Yüksek hacimli kelimeler
            if volume >= high_threshold:
                categories['primary_keywords'].append(kw)
                continue

            # Orta hacimli kelimeler
            if volume >= med_threshold:
                categories['secondary_keywords'].append(kw)
                continue

            # Kalan kelimeleri hacimlerine göre dağıt
            if len(categories['primary_keywords']) < 10:
                categories['primary_keywords'].append(kw)
            elif len(categories['secondary_keywords']) < 10:
                categories['secondary_keywords'].append(kw)
            else:
                categories['long_tail_keywords'].append(kw)

        # Her kategoriden en az 5 kelime olmasını sağla
        min_keywords = 5

        # Kategoriler arası kelime aktarımı
        for from_cat, to_cat in [
            ('secondary_keywords', 'primary_keywords'),
            ('long_tail_keywords', 'secondary_keywords')
        ]:
            if len(categories[to_cat]) < min_keywords and categories[from_cat]:
                move_count = min(
                    min_keywords - len(categories[to_cat]),
                    len(categories[from_cat])
                )
                categories[to_cat].extend(categories[from_cat][:move_count])
                categories[from_cat] = categories[from_cat][move_count:]

        # Her kategoriyi en fazla 15 kelime ile sınırla
        max_keywords = 15
        for cat in categories:
            categories[cat] = categories[cat][:max_keywords]

        return categories

@method_decorator(csrf_exempt, name='dispatch')
class CompetitorAnalysisView(LoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse({'message': 'GET method is not supported'}, status=405)

    def post(self, request):
        try:
            data = json.loads(request.body)
            keyword = data.get('keyword')
            if not keyword:
                return JsonResponse({'error': 'Anahtar kelime gerekli'}, status=400)

            semrush = SEMrushAPI()
            competitors = semrush.get_competitors(keyword)

            if competitors:
                return JsonResponse({
                    'success': True,
                    'competitors': competitors
                })

            return JsonResponse({'error': 'Rakip analizi başarısız'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Geçersiz JSON verisi'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ContentBriefView(LoginRequiredMixin, View):
    def post(self, request):
        keyword = request.POST.get('keyword')
        if not keyword:
            return JsonResponse({'error': 'Anahtar kelime gerekli'}, status=400)

        semrush = SEMrushAPI()

        # Anahtar kelime analizi
        keyword_analysis = semrush.analyze_keyword(keyword)
        if not keyword_analysis:
            return JsonResponse({'error': 'Anahtar kelime analizi başarısız'}, status=400)

        # Rakip analizi
        competitors = semrush.get_competitors(keyword)
        competitor_insights = []

        for comp in competitors:
            content_analysis = semrush.analyze_content(comp['url'])
            if content_analysis:
                competitor_insights.append({
                    'url': comp['url'],
                    'title': comp['title'],
                    'position': comp['position'],
                    'word_count': content_analysis['word_count'],
                    'meta_title': content_analysis['meta_title'],
                    'meta_description': content_analysis['meta_description']
                })

        # İçerik özeti oluştur
        brief = {
            'keyword_data': keyword_analysis,
            'competitors': competitor_insights,
            'recommended_length': sum(c['word_count'] for c in competitor_insights) // len(competitor_insights) if competitor_insights else 1000,
            'suggested_topics': [comp['title'] for comp in competitors[:3]]
        }

        return JsonResponse({
            'success': True,
            'brief': brief
        })

def keyword_analysis(request):
    semrush = SEMrushAPI()
    try:
        if not semrush.test_connection():
            logger.error("SEMrush API bağlantı testi başarısız")
            messages.error(request, "SEMrush API bağlantısı başarısız. Lütfen daha sonra tekrar deneyin.")
            return render(request, 'content_manager/keyword_analysis.html', {'error': 'API bağlantı hatası'})
        
        results = None
        if request.method == 'POST':
            keyword = request.POST.get('keyword')
            if keyword:
                keyword_data = semrush.analyze_keyword(keyword)
                if keyword_data:
                    results = {
                        'keyword': keyword,
                        'volume': keyword_data.get('volume', 0),
                        'cpc': keyword_data.get('cpc', 0),
                        'competition': keyword_data.get('competition', 0),
                        'trend': keyword_data.get('trend', {'average': 0}),
                        'related_keywords': semrush.get_related_keywords(keyword),
                        'competitors': semrush.get_competitors(keyword)
                    }
                else:
                    messages.warning(request, "Anahtar kelime için veri bulunamadı.")
        
        return render(request, 'content_manager/keyword_analysis.html', {'results': results})
        
    except Exception as e:
        logger.exception("Keyword analizi sırasında hata oluştu")
        messages.error(request, f"Bir hata oluştu: {str(e)}")
        return render(request, 'content_manager/keyword_analysis.html', {'error': 'Beklenmeyen bir hata oluştu'})

def analyze_keywords(self, keywords):
    try:
        print("\n=== SEMrush ANALİZİ BAŞLIYOR ===")
        semrush = SEMrushAPI()
        result = semrush.analyze_keywords(keywords)

        if "error" in result:
            print(f"SEMrush Analiz Hatası: {result['error']}")
            return None

        print("SEMrush analizi tamamlandı")
        return result

    except Exception as e:
        print(f"SEMrush Analiz Exception: {str(e)}")
        return None