from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SEGURIDAD BÁSICA
# ==========================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'alexandra-farms-2026-!@#$xK9mP2qL8nR4vT6wY1uI3oE5aS7dF0gH')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = [
    'AlexandraFarms.pythonanywhere.com',
    '127.0.0.1',
    'localhost'
]

# ==========================================
# APLICACIONES
# ==========================================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'cuentas',
    'reclamos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Alexaticks.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Alexaticks.wsgi.application'

# ==========================================
# BASE DE DATOS
# ==========================================
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==========================================
# VALIDACIÓN DE CONTRASEÑAS
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================
# INTERNACIONALIZACIÓN
# ==========================================
LANGUAGE_CODE = 'es-eu'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==========================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# LOGIN
# ==========================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# ==========================================
# JAZZMIN
# ==========================================
JAZZMIN_SETTINGS = {
    'site_title': 'Mi Panel Admin',
    'site_header': 'Administración',
    'site_brand': 'Mi Proyecto',
    'welcome_sign': 'Bienvenido al panel',
    'copyright': 'Mi empresa',
    'topmenu_links': [
        {'name': 'Inicio', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'model': 'auth.User'},
    ],
}

# ==========================================
# CONFIGURACIÓN DE CORREO (Gmail)
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'adminalexandrafarms@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'cuhv tbgy sgia nfog')
DEFAULT_FROM_EMAIL = f'Alexandra Farms <{EMAIL_HOST_USER}>'

# ==========================================
# SEGURIDAD — HEADERS Y PROTECCIONES
# ==========================================
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_REFERRER_POLICY = 'same-origin'

# PythonAnywhere maneja SSL externamente
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ==========================================
# PROTECCIÓN OWASP
# ==========================================
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# ==========================================
# LOGS DE SEGURIDAD
# ==========================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'seguridad': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'archivo_seguridad': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'seguridad.log',
            'formatter': 'seguridad',
        },
        'consola': {
            'class': 'logging.StreamHandler',
            'formatter': 'seguridad',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['archivo_seguridad', 'consola'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['archivo_seguridad'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}