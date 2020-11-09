import os
from datetime import timedelta

from environs import Env
from marshmallow.validate import OneOf, Email


# Read .env if any
env = Env(expand_vars=True)
env.read_env(env.path("DOTENV", ".env"), override=False)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_path(rel: str) -> str:
    """Helper to build paths from the project's root"""
    return os.path.join(BASE_DIR, rel.replace('/', os.path.sep))


# --------------------------------------------------------------------------
#       Application Configuration
# --------------------------------------------------------------------------

EXPORTS_DIR = make_path('exports')

MAX_ONGOING_TIME = timedelta(minutes=15)
MAX_PAYMENT_TIME = timedelta(hours=1)
MAX_VALIDATION_TIME = timedelta(days=30)

API_MODEL_CACHE_TIMEOUT = timedelta(minutes=30)

VALID_TVA = {0, 5.5, 10, 20}

# --------------------------------------------------------------------------
#       Services Configuration
# --------------------------------------------------------------------------

# PayUTC Payment services
PAYUTC = {
    'app_key': env.str("PAYUTC_APP_KEY"),
    'mail': env.str("PAYUTC_MAIL", validate=[Email()]),
    'password': env.str("PAYUTC_PASSWORD"),
}

# Portail des Assos OAuth config
OAUTH = {
    'portal': {
        'client_id':        env.str("PORTAL_ID"),
        'client_secret':    env.str("PORTAL_KEY"),
        'redirect_uri':     env.str("PORTAL_CALLBACK"),
        'base_url':         'https://assos.utc.fr/api/v1/',
        'authorize_url':    'https://assos.utc.fr/oauth/authorize',
        'access_token_url': 'https://assos.utc.fr/oauth/token',
        'login_url':        'https://assos.utc.fr/login',
        'logout_url':       'https://assos.utc.fr/logout',
        # TODO Set scope to user-get-assos-members-joined-now',
        'scope':            'user-get-assos user-get-info user-get-roles',
    },
}

# Database server
DATABASES = {
    'default': env.dj_db_url("DATABASE_URL"),
}

# Email server
email = env.dj_email_url("EMAIL_URL")
EMAIL_HOST = email["EMAIL_HOST"]
EMAIL_PORT = email["EMAIL_PORT"]
EMAIL_HOST_USER = email["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email["EMAIL_HOST_PASSWORD"]
EMAIL_USE_SSL = email["EMAIL_USE_SSL"]
EMAIL_USE_TLS = email["EMAIL_USE_TLS"]

# --------------------------------------------------------------------------
#       Debug & Security
# --------------------------------------------------------------------------

STAGE = env.str("STAGE", "prod", validate=[OneOf(["prod", "test", "dev"])])
DEBUG = STAGE in {"dev", "test"}

SECRET_KEY = env.str("SECRET_KEY")

# Base url
BASE_URL = env.str("BASE_URL", None)
FORCE_SCRIPT_NAME = BASE_URL

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["assos.utc.fr"])
HTTPS_ENABLED = env.bool("HTTPS_ENABLED", STAGE == "prod")
SECURE_SSL_REDIRECT = HTTPS_ENABLED
SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = HTTPS_ENABLED
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Cross Site Request Foregery protection
CSRF_COOKIE_SECURE = HTTPS_ENABLED
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS
CSRF_COOKIE_HTTPONLY = False      # False to enable the use of cookies in ajax requests
CSRF_USE_SESSIONS = False         # False to enable the use of cookies in ajax requests

# Cross-Origin Resource Sharing protection
CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", [ f"https://{url}" for url in ALLOWED_HOSTS ])

if env.bool("RUN_THROUGH_PROXY", False):
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --------------------------------------------------------------------------
#       Django REST Configuration
# --------------------------------------------------------------------------

BROWSABLE_API_WITH_FORMS = env.bool("BROWSABLE_API_WITH_FORMS", DEBUG)
APPEND_SLASH = False
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.oauth.OAuthAuthentication',
    ),
    'EXCEPTION_HANDLER': 'core.exceptions.exception_handler',

    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'core.views.Pagination',

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'core.utils.BrowsableAPIRenderer',
    ),
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ),
}


# --------------------------------------------------------------------------
#       Django Configuration
# --------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django_extensions',
    # Django REST
    'rest_framework',
    'corsheaders',
    # Woolly
    'woolly_api.admin.AdminConfig',
    'core',
    'authentication',
    'sales',
    'payment',
]

# Urls & WSGI
ROOT_URLCONF = 'woolly_api.urls'
WSGI_APPLICATION = 'woolly_api.wsgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Authentication
LOGIN_URL = 'login'
AUTH_USER_MODEL = 'authentication.User'

# Only to access web admin panel
AUTHENTICATION_BACKENDS = (
    'authentication.oauth.OAuthBackend',
)

AUTH_PASSWORD_VALIDATORS = (
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
)

# Internationalization
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'


# --------------------------------------------------------------------------
#       Static Files & Templates
# --------------------------------------------------------------------------

STATIC_URL = f'{BASE_URL}/static/' if BASE_URL else '/static/'
STATIC_ROOT = make_path('static/')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            make_path('templates/'),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]


# --------------------------------------------------------------------------
#       Logging
# --------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] {levelname} - {message}',
            'style': '{',
        },
        'verbose': {
            'format': '[{asctime}] {levelname} in {filename}@{lineno} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': make_path('woolly.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
        },
        'woolly': {
            'handlers': ['console', 'file'],
            'level': env.log_level("LOG_LEVEL", "INFO"),
            'propagate': True,
        }
    },
}
