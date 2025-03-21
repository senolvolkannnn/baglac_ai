import re
from django.utils.text import slugify
from django.conf import settings
import openai

def generate_unique_slug(model_instance, title, slug_field="slug"):
    """
    Verilen başlıktan benzersiz bir slug oluşturur
    """
    slug = slugify(title)
    unique_slug = slug
    extension = 1
    
    ModelClass = model_instance.__class__
    while ModelClass._default_manager.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{extension}"
        extension += 1
    
    return unique_slug

def sanitize_html(html_content):
    """
    HTML içeriğini temizler ve güvenli hale getirir
    """
    # Temel HTML temizleme işlemleri
    cleaned = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
    cleaned = re.sub(r'javascript:', '', cleaned)
    cleaned = re.sub(r'on\w+=".*?"', '', cleaned)
    return cleaned

def get_openai_response(prompt, max_tokens=1000):
    """
    OpenAI API'sini kullanarak yanıt alır
    """
    try:
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}" 