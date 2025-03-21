from typing import Dict, List, Any
import re
from bs4 import BeautifulSoup
from django.conf import settings
import requests
from .models import SEOAnalysis, KeywordAnalysis

class SEOAnalyzer:
    def __init__(self, content):
        self.content = content
        self.text = BeautifulSoup(content.content, 'html.parser').get_text()
        self.keywords = [kw.strip() for kw in content.keywords.split(',')]
        self.metrics = []
        self.score = 0

    def analyze(self) -> Dict[str, Any]:
        """Tüm SEO analizlerini gerçekleştirir ve sonuçları döndürür."""
        self._analyze_title()
        self._analyze_meta_description()
        self._analyze_keyword_density()
        self._analyze_content_length()
        self._analyze_headings()
        self._analyze_links()
        self._calculate_score()
        
        return {
            'score': self.score,
            'metrics': self.metrics
        }

    def _analyze_title(self):
        """Başlık uzunluğunu ve anahtar kelime kullanımını analiz eder."""
        title = self.content.seo_title or self.content.title
        title_length = len(title)
        
        status = 'success'
        suggestions = []
        
        if title_length < 30:
            status = 'warning'
            suggestions.append('Başlık çok kısa. 50-60 karakter arasında olması önerilir.')
        elif title_length > 60:
            status = 'warning'
            suggestions.append('Başlık çok uzun. 50-60 karakter arasında olması önerilir.')
            
        # Anahtar kelime kontrolü
        if not any(kw.lower() in title.lower() for kw in self.keywords):
            status = 'warning'
            suggestions.append('Başlıkta anahtar kelime kullanılmamış.')
            
        self.metrics.append({
            'name': 'Başlık Analizi',
            'description': 'Başlık uzunluğu ve anahtar kelime kullanımı',
            'value': f'{title_length} karakter',
            'status': status,
            'suggestions': suggestions
        })

    def _analyze_meta_description(self):
        """Meta açıklama uzunluğunu ve anahtar kelime kullanımını analiz eder."""
        description = self.content.seo_description
        if not description:
            self.metrics.append({
                'name': 'Meta Açıklama',
                'description': 'Meta açıklama analizi',
                'value': 'Eksik',
                'status': 'error',
                'suggestions': ['Meta açıklama eklenmeli.']
            })
            return
            
        desc_length = len(description)
        status = 'success'
        suggestions = []
        
        if desc_length < 120:
            status = 'warning'
            suggestions.append('Meta açıklama çok kısa. 150-160 karakter arasında olması önerilir.')
        elif desc_length > 160:
            status = 'warning'
            suggestions.append('Meta açıklama çok uzun. 150-160 karakter arasında olması önerilir.')
            
        if not any(kw.lower() in description.lower() for kw in self.keywords):
            status = 'warning'
            suggestions.append('Meta açıklamada anahtar kelime kullanılmamış.')
            
        self.metrics.append({
            'name': 'Meta Açıklama Analizi',
            'description': 'Meta açıklama uzunluğu ve anahtar kelime kullanımı',
            'value': f'{desc_length} karakter',
            'status': status,
            'suggestions': suggestions
        })

    def _analyze_keyword_density(self):
        """Anahtar kelime yoğunluğunu analiz eder."""
        word_count = len(self.text.split())
        if word_count == 0:
            return
            
        for keyword in self.keywords:
            keyword = keyword.lower()
            keyword_count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', self.text.lower()))
            density = (keyword_count * 100) / word_count
            
            status = 'success'
            suggestions = []
            
            if density < 0.5:
                status = 'warning'
                suggestions.append(f'"{keyword}" anahtar kelimesi çok az kullanılmış. %1-3 arası önerilir.')
            elif density > 3:
                status = 'warning'
                suggestions.append(f'"{keyword}" anahtar kelimesi çok fazla kullanılmış. Aşırı kullanım spam olarak algılanabilir.')
                
            self.metrics.append({
                'name': f'Anahtar Kelime Yoğunluğu: {keyword}',
                'description': 'İçerikte anahtar kelime kullanım oranı',
                'value': f'%{density:.1f}',
                'status': status,
                'suggestions': suggestions
            })

    def _analyze_content_length(self):
        """İçerik uzunluğunu analiz eder."""
        word_count = len(self.text.split())
        status = 'success'
        suggestions = []
        
        if word_count < 300:
            status = 'error'
            suggestions.append('İçerik çok kısa. En az 300 kelime önerilir.')
        elif word_count < 600:
            status = 'warning'
            suggestions.append('İçerik biraz kısa. 600+ kelime önerilir.')
            
        self.metrics.append({
            'name': 'İçerik Uzunluğu',
            'description': 'Toplam kelime sayısı',
            'value': f'{word_count} kelime',
            'status': status,
            'suggestions': suggestions
        })

    def _analyze_headings(self):
        """Başlık hiyerarşisini analiz eder."""
        soup = BeautifulSoup(self.content.content, 'html.parser')
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))
        h3_count = len(soup.find_all('h3'))
        
        status = 'success'
        suggestions = []
        
        if h1_count == 0:
            status = 'warning'
            suggestions.append('H1 başlığı kullanılmamış.')
        elif h1_count > 1:
            status = 'warning'
            suggestions.append('Birden fazla H1 başlığı kullanılmış. Tek H1 başlığı önerilir.')
            
        if h2_count == 0:
            status = 'warning'
            suggestions.append('H2 başlıkları kullanılmamış. Alt başlıklar için H2 kullanın.')
            
        self.metrics.append({
            'name': 'Başlık Hiyerarşisi',
            'description': 'HTML başlık etiketlerinin kullanımı',
            'value': f'H1: {h1_count}, H2: {h2_count}, H3: {h3_count}',
            'status': status,
            'suggestions': suggestions
        })

    def _analyze_links(self):
        """İç ve dış bağlantıları analiz eder."""
        soup = BeautifulSoup(self.content.content, 'html.parser')
        links = soup.find_all('a')
        internal_links = len([l for l in links if l.get('href', '').startswith('/')])
        external_links = len([l for l in links if l.get('href', '').startswith('http')])
        
        status = 'success'
        suggestions = []
        
        if internal_links == 0:
            status = 'warning'
            suggestions.append('İç bağlantı kullanılmamış. Site içi bağlantılar SEO için önemlidir.')
            
        if external_links == 0:
            status = 'warning'
            suggestions.append('Dış bağlantı kullanılmamış. Güvenilir kaynaklara bağlantı vermek faydalı olabilir.')
            
        self.metrics.append({
            'name': 'Bağlantı Analizi',
            'description': 'İç ve dış bağlantıların kullanımı',
            'value': f'İç: {internal_links}, Dış: {external_links}',
            'status': status,
            'suggestions': suggestions
        })

    def _calculate_score(self):
        """Metriklerden genel SEO skorunu hesaplar."""
        total_score = 0
        max_score = len(self.metrics) * 100
        
        for metric in self.metrics:
            if metric['status'] == 'success':
                total_score += 100
            elif metric['status'] == 'warning':
                total_score += 50
                
        self.score = int((total_score / max_score) * 100) if max_score > 0 else 0

    def save_analysis(self) -> SEOAnalysis:
        """Analiz sonuçlarını veritabanına kaydeder."""
        analysis = SEOAnalysis.objects.create(
            content=self.content,
            score=self.score,
            meta_title_length=len(self.content.seo_title or self.content.title),
            meta_description_length=len(self.content.seo_description or ''),
            word_count=len(self.text.split())
        )
        
        # Anahtar kelime analizlerini kaydet
        for keyword in self.keywords:
            keyword_count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', self.text.lower()))
            KeywordAnalysis.objects.create(
                analysis=analysis,
                keyword=keyword,
                count=keyword_count,
                density=keyword_count * 100 / len(self.text.split()) if self.text else 0
            )
            
        return analysis 