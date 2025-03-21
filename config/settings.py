import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here')  # Geçici olarak default değer ekledik

# Debug'ı geçici olarak tekrar True yapalım
DEBUG = True

# ALLOWED_HOSTS ayarını güncelleyelim
ALLOWED_HOSTS = ['senolvolkannn.pythonanywhere.com', 'localhost', '127.0.0.1']

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/home/senolvolkannn/baglac_ai/staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/senolvolkannn/baglac_ai/media'

# Güvenlik ayarları
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CSRF güvenlik ayarı ekleyelim
CSRF_TRUSTED_ORIGINS = ['https://senolvolkannn.pythonanywhere.com']

# HTTPS header ayarını kaldıralım
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps
    'tailwind',
    'theme',
    'django_htmx',
    'tinymce',
    
    # Kendi uygulamalarımız
    'apps.accounts.apps.AccountsConfig',
    'apps.content_manager.apps.ContentManagerConfig',
    'apps.core.apps.CoreConfig',
    'apps.seo_analyzer.apps.SeoAnalyzerConfig',
    'apps.media_library.apps.MediaLibraryConfig',
    'apps.analytics.apps.AnalyticsConfig',
] 

# OpenAI Ayarları
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set!")
OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID', 'asst_g4F5HsCMDX38iHrsMkAgPhGu')

# SEMrush API Ayarları
SEMRUSH_API_KEY = os.getenv('SEMRUSH_API_KEY', '').strip()
if not SEMRUSH_API_KEY:
    print("WARNING: SEMRUSH_API_KEY is not set!")

# Timeout ayarları
REQUEST_TIMEOUT = 300  # 5 dakika
OPENAI_REQUEST_TIMEOUT = 180  # 3 dakika

# Middleware ayarları
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

# Template ayarları
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database ayarları
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Anthropic API Ayarları
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '').strip()
if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY is not set!")
else:
    print(f"Anthropic API Key loaded: {ANTHROPIC_API_KEY[:10]}...")