"""
Django settings for learning_platform project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import os
import secrets

# Thử lấy SECRET_KEY từ biến môi trường
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Nếu không có SECRET_KEY trong biến môi trường, tạo một key mới
if not SECRET_KEY:
    # Chỉ hiển thị cảnh báo trong môi trường phát triển
    if os.environ.get('DJANGO_DEBUG', 'True') == 'True':
        print("WARNING: No SECRET_KEY set in environment variables. Using a random key.")
        print("This is fine for development but not for production.")

    # Tạo một SECRET_KEY ngẫu nhiên mới
    SECRET_KEY = secrets.token_hex(32)  # 64 ký tự hex

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Lấy danh sách ALLOWED_HOSTS từ biến môi trường hoặc sử dụng giá trị mặc định an toàn
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]')
ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(',')

# Bảo mật cho cookie và session
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 năm
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "crispy_forms",
    "crispy_bootstrap4",
    "csp",  # Content Security Policy
    "channels",  # Django Channels for WebSocket
    "django_htmx",  # HTMX integration

    # Custom apps
    "accounts",
    "content",
    "flashcards",
    "quizzes",
    "memory_bank",
    "advanced_learning",
    "django_summernote",
    "notifications",  # Ứng dụng thông báo mới
    "learning_goals",  # Ứng dụng mục tiêu học tập
    "achievements",  # Ứng dụng thành tích và phần thưởng
    "personalization",  # Ứng dụng cá nhân hóa
    "ai_assistant",  # Ứng dụng trợ lý học tập AI
    "learning_chatbot",  # Ứng dụng chatbot hỗ trợ học tập
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",  # Content Security Policy middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",  # HTMX middleware
    "learning_platform.middleware.SecurityHeadersMiddleware",  # Middleware bảo mật tùy chỉnh
]

ROOT_URLCONF = "learning_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "learning_platform.wsgi.application"
ASGI_APPLICATION = "learning_platform.asgi.application"

# Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Kết nối với Supabase PostgreSQL - Chỉ sử dụng biến môi trường, không lưu thông tin nhạy cảm
SUPABASE_DB_USER = os.environ.get('SUPABASE_DB_USER')
SUPABASE_DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD')
SUPABASE_DB_HOST = os.environ.get('SUPABASE_DB_HOST')
SUPABASE_DB_PORT = os.environ.get('SUPABASE_DB_PORT', '5432')  # Port mặc định an toàn để giữ lại
SUPABASE_DB_NAME = os.environ.get('SUPABASE_DB_NAME', 'postgres')  # Tên database mặc định an toàn để giữ lại
SUPABASE_DB_SCHEMA = os.environ.get('SUPABASE_DB_SCHEMA', 'public')  # Schema mặc định an toàn để giữ lại

# Kiểm tra xem các biến môi trường bắt buộc đã được thiết lập chưa
if not all([SUPABASE_DB_USER, SUPABASE_DB_PASSWORD, SUPABASE_DB_HOST]):
    if DEBUG:
        print("Cảnh báo: Thiếu thông tin kết nối Supabase. Hãy kiểm tra file .env")
    else:
        raise Exception("Thiếu thông tin kết nối Supabase. Hãy kiểm tra file .env")

# Cấu hình Supabase Connection String (dùng cho các công cụ bên ngoài)
SUPABASE_CONNECTION_STRING = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}?sslmode=require"

# Cấu hình cơ sở dữ liệu
# Sử dụng Supabase PostgreSQL nếu có đủ thông tin kết nối
# Nếu không, sử dụng SQLite cho môi trường phát triển
if all([SUPABASE_DB_USER, SUPABASE_DB_PASSWORD, SUPABASE_DB_HOST]):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': SUPABASE_DB_NAME,
            'USER': SUPABASE_DB_USER,
            'PASSWORD': SUPABASE_DB_PASSWORD,
            'HOST': SUPABASE_DB_HOST,
            'PORT': SUPABASE_DB_PORT,
            'OPTIONS': {
                'sslmode': 'require',
                'options': f'-c search_path={SUPABASE_DB_SCHEMA}',
            },
        }
    }
    print("Sử dụng Supabase PostgreSQL")
else:
    # Sử dụng SQLite cho môi trường phát triển nếu thiếu thông tin kết nối Supabase
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    if DEBUG:
        print("Sử dụng SQLite cho môi trường phát triển")
    else:
        print("Cảnh báo: Đang sử dụng SQLite trong môi trường production!")


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication settings
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# Django Summernote settings
SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '100%',
        'height': '480px',
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
        'disable_attachment': False,  # Set to True to disable attachment completely
    },
    'attachment_storage_class': 'django.core.files.storage.FileSystemStorage',
    'attachment_filesize_limit': 5 * 1024 * 1024,  # Giới hạn 5MB
    'attachment_require_authentication': True,  # Yêu cầu đăng nhập để tải lên file
    'attachment_upload_to': 'summernote_uploads/%Y/%m/%d/',  # Đường dẫn lưu trữ có cấu trúc
    'attachment_file_types': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'],  # Chỉ cho phép hình ảnh và PDF
    'attachment_upload_to_s3': False,  # Không sử dụng S3
    'attachment_absolute_uri': False,  # Không sử dụng URI tuyệt đối
    'summernote_sanitizer': {
        'tags': ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'strong', 'em', 'br', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'span'],
        'attributes': {
            '*': ['style', 'class'],
            'a': ['href', 'target'],
            'img': ['src', 'alt', 'width', 'height'],
        },
        'styles': [
            'font-family', 'font-size', 'font-weight', 'color', 'text-align', 'background-color',
            'margin', 'padding', 'width', 'height', 'border', 'border-radius'
        ],
    },
}

# Content Security Policy settings
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.jsdelivr.net"),
        'style-src': ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'img-src': ("'self'", "data:", "blob:"),
        'connect-src': ("'self'",),
        'frame-src': ("'self'",),
        'object-src': ("'none'",),
        'base-uri': ("'self'",),
    }
}

# Password validation settings
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Cấu hình bảo mật cho file upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Cấu hình Supabase API - Chỉ sử dụng biến môi trường, không lưu thông tin nhạy cảm
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_SECRET = os.environ.get('SUPABASE_SECRET')

# Kiểm tra xem các biến môi trường Supabase API đã được thiết lập chưa
if not all([SUPABASE_URL, SUPABASE_KEY]):
    if DEBUG:
        print("Cảnh báo: Thiếu thông tin Supabase API. Hãy kiểm tra file .env")
    else:
        raise Exception("Thiếu thông tin Supabase API. Hãy kiểm tra file .env")

# Cấu hình Email
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@learningplatform.com')

# URL của trang web (dùng cho email)
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')

# Cấu hình OpenAI API
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', 1000))
OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', 0.7))
