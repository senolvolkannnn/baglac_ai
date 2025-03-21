import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SEMrushAPI:
    def __init__(self):
        """SEMrush API istemcisini başlatır"""
        self.api_key = settings.SEMRUSH_API_KEY
        self._validate_api_key()
        
        self.base_url = "https://api.semrush.com"
        self.default_database = "tr"
        
        logger.info(f"SEMrush API başlatıldı. API Anahtarı: {self.api_key[:8]}...")

    def _validate_api_key(self):
        """API anahtarının geçerliliğini kontrol eder"""
        if not self.api_key:
            logger.error("SEMrush API anahtarı yapılandırılmamış!")
            raise ValueError("SEMrush API anahtarı gerekli")

    def _make_request(self, params: Dict) -> Optional[str]:
        """API isteği yapar ve yanıtı döndürür"""
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            logger.debug(f"API Yanıtı - Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"SEMrush API Hatası: {response.text}")
                return None
                
            return response.text

        except Exception as e:
            logger.error(f"API isteği hatası: {str(e)}")
            return None

    def _parse_csv_response(self, response_text: str) -> List[Dict]:
        """CSV formatındaki API yanıtını parse eder"""
        try:
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            if not lines:
                return []

            headers = [h.strip() for h in lines[0].split(';')]
            
            parsed_data = []
            for line in lines[1:]:
                values = [v.strip() for v in line.split(';')]
                if len(values) != len(headers):
                    continue
                    
                row_data = dict(zip(headers, values))
                parsed_data.append(row_data)

            return parsed_data

        except Exception as e:
            logger.error(f"CSV parse hatası: {str(e)}")
            return []

    def analyze_keyword(self, keyword: str, database: str = None) -> Optional[Dict]:
        """Anahtar kelime analizi yapar"""
        try:
            params = {
                "type": "phrase_this",
                "key": self.api_key,
                "phrase": keyword,
                "export_columns": "Ph,Nq,Cp,Co,Nr,Td",
                "database": database or self.default_database
            }
            
            response = self._make_request(params)
            if not response:
                return None

            data = self._parse_csv_response(response)
            if not data:
                return None

            row = data[0]
            return {
                'keyword': row.get('Keyword', ''),
                'volume': int(row.get('Search Volume', '0').replace(',', '')),
                'cpc': float(row.get('CPC', '0').replace('$', '').replace(',', '')),
                'competition': float(row.get('Competition', '0').replace('%', '')) / 100,
                'results': int(row.get('Number of Results', '0').replace(',', '')),
                'trend': row.get('Trends', '').split(',') if row.get('Trends') else []
            }

        except Exception as e:
            logger.error(f"Anahtar kelime analizi hatası: {str(e)}")
            return None

    def get_related_keywords(self, keyword: str, limit: int = 20) -> List[Dict]:
        """İlgili anahtar kelimeleri getirir"""
        try:
            params = {
                "type": "phrase_related",
                "key": self.api_key,
                "phrase": keyword,
                "export_columns": "Ph,Nq,Cp,Co,Rr,Td,Fk",
                "database": self.default_database,
                "display_limit": limit,
                "display_sort": "nq_desc"
            }
            
            response = self._make_request(params)
            if not response:
                return []

            data = self._parse_csv_response(response)
            
            related_keywords = []
            for row in data:
                try:
                    keyword_data = {
                        'keyword': row.get('Keyword', ''),
                        'volume': int(row.get('Search Volume', '0').replace(',', '')),
                        'cpc': float(row.get('CPC', '0').replace('$', '').replace(',', '')),
                        'competition': float(row.get('Competition', '0').replace('%', '')) / 100,
                        'relevance': float(row.get('Related Relevance', '0')),
                        'trend': row.get('Trends', '').split(',') if row.get('Trends') else [],
                        'features': row.get('SERP Features', '').split(',') if row.get('SERP Features') else []
                    }
                    related_keywords.append(keyword_data)
                except (ValueError, KeyError) as e:
                    logger.error(f"İlgili kelime parse hatası: {str(e)} - Veri: {row}")
                    continue

            return related_keywords

        except Exception as e:
            logger.error(f"İlgili kelimeler hatası: {str(e)}")
            return []

    def get_competitors(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Organik rakip analizi yapar"""
        try:
            params = {
                "type": "phrase_organic",
                "key": self.api_key,
                "phrase": keyword,
                "export_columns": "Dn,Ur,Po,Fk",
                "database": self.default_database,
                "display_limit": limit
            }
            
            response = self._make_request(params)
            if not response:
                return []

            data = self._parse_csv_response(response)
            
            return [
                {
                    'domain': row.get('Domain', ''),
                    'url': row.get('Url', ''),
                    'position': int(row.get('Position', '0')),
                    'features': row.get('SERP Features', '').split(',') if row.get('SERP Features') else []
                }
                for row in data
            ]

        except Exception as e:
            logger.error(f"Rakip analizi hatası: {str(e)}")
            return []

    def test_connection(self) -> bool:
        """API bağlantısını test eder"""
        try:
            params = {
                "type": "phrase_this",
                "key": self.api_key,
                "phrase": "test",
                "export_columns": "Ph,Nq",
                "database": self.default_database
            }
            
            response = self._make_request(params)
            return response is not None

        except Exception as e:
            logger.error(f"Bağlantı testi hatası: {str(e)}")
            return False

    def get_remaining_units(self) -> Optional[int]:
        """Kalan API kredisini kontrol eder"""
        try:
            params = {
                "type": "api_units",
                "key": self.api_key
            }
            
            response = self._make_request(params)
            if response:
                return int(response.strip())
            return None

        except Exception as e:
            logger.error(f"API kredi kontrolü hatası: {str(e)}")
            return None 