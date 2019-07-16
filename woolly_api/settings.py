"""
Django settings for woolly_api project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
from woolly_api import settings_confidential as confidentials

# Build paths inside the project like this: use make_path helper or os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_path(rel):
	return os.path.join(BASE_DIR, rel.replace('/', os.path.sep))

# --------------------------------------------------------------------------
# 		Services Configuration
# --------------------------------------------------------------------------


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = confidentials.SECRET_KEY

# Payutc & Ginger config
PAYUTC_KEY = confidentials.PAYUTC_KEY
PAYUTC_TRANSACTION_BASE_URL = 'https://payutc.nemopay.net/validation?tra_id='
GINGER_KEY = confidentials.GINGER_KEY
GINGER_SERVER_URL = 'https://assos.utc.fr/ginger/v1/'

# Portail des Assos config
OAUTH = {
	'portal': {
		'client_id': 		confidentials.PORTAL['id'],
		'client_secret': 	confidentials.PORTAL['key'],
		'redirect_uri': 	confidentials.PORTAL['callback'],
		'base_url': 		'https://assos.utc.fr/api/v1/',
		'authorize_url': 	'https://assos.utc.fr/oauth/authorize',
		'access_token_url': 'https://assos.utc.fr/oauth/token',
		'login_url': 		'https://assos.utc.fr/login',
		'logout_url': 		'https://assos.utc.fr/logout',
		'scope': 			'user-get-info user-get-roles user-get-assos-members-joined-now'
	}
}

# --------------------------------------------------------------------------
# 		Cors & Debug
# --------------------------------------------------------------------------

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = confidentials.DEBUG
ALLOWED_HOSTS = confidentials.ALLOWED_HOSTS

# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = False # False to enable the use of cookies in ajax requests
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db' # cache or cached_db

# CORS headers config
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = (
	'GET',
	'POST',
	'PUT',
	'PATCH',
	'OPTIONS',
	'DELETE',
)

# necessary in addition to the whitelist for protected requests
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = False # False to enable the use of cookies in ajax requests
CSRF_USE_SESSIONS = False  # Useful ??
CSRF_TRUSTED_ORIGINS = ALLOWED_HOSTS


# --------------------------------------------------------------------------
# 		Django REST Configuration
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'authentication.oauth.OAuthAPI',
	),

	'PAGE_SIZE': 10,
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',

	'DEFAULT_PARSER_CLASSES': (
		'rest_framework.parsers.JSONParser',								# Simple JSON
		'rest_framework.parsers.FormParser',
		'rest_framework.parsers.MultiPartParser'
	),
	'DEFAULT_RENDERER_CLASSES': (
		'rest_framework.renderers.JSONRenderer',						# Simple JSON
		# 'rest_framework.renderers.BrowsableAPIRenderer',
		'core.utils.BrowsableAPIRendererWithoutForms',			# For performance testing
	),
	
	# 'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',

	'TEST_REQUEST_RENDERER_CLASSES': (
		'rest_framework.renderers.MultiPartRenderer',
		'rest_framework.renderers.JSONRenderer',
		'rest_framework.renderers.TemplateHTMLRenderer'
	),
}

VIEWSET = {
	'list': {
		'get': 'list',
		'post': 'create'
	},
	'detail': {
		'get': 'retrieve',
		'put': 'update',
		'patch': 'partial_update',
		'delete': 'destroy'
	}
}

# --------------------------------------------------------------------------
# 		Django Configuration
# --------------------------------------------------------------------------

# Database : https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
	'default': confidentials.DATABASE,
	'sqlite': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'db.sqlite3',
	}
}
if 'test' in sys.argv and 'sqlite' in DATABASES: # Test database
	DATABASES['default'] = DATABASES.pop('sqlite')

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
	'woolly_api.admin.AdminConfig', # Replace 'django.contrib.admin',
	'core',
	'authentication',
	'sales',
	'payment',
]

# Urls & WSGI
ROOT_URLCONF = 'woolly_api.urls'
WSGI_APPLICATION = 'woolly_api.wsgi.application'

MIDDLEWARE = [
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
]

# Authentication
AUTH_USER_MODEL = 'authentication.User'

# Only to access web admin panel
AUTHENTICATION_BACKENDS = None

# Password validation : https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Mails
EMAIL_HOST = confidentials.EMAIL.get('host', 'localhost')
EMAIL_PORT = confidentials.EMAIL.get('port', 25)
EMAIL_HOST_USER = confidentials.EMAIL.get('user', '')
EMAIL_HOST_PASSWORD = confidentials.EMAIL.get('pwd', '')
EMAIL_USE_SSL = confidentials.EMAIL.get('ssl', False)
EMAIL_USE_TLS = confidentials.EMAIL.get('tls', False)


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'


# --------------------------------------------------------------------------
# 		Static Files & Templates
# --------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = make_path('static/')
# STATICFILES_DIRS = (
# 	make_path('assets/'),
# )

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
# 		Logging
# --------------------------------------------------------------------------

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '[{asctime}] {levelname} in {filename}@{lineno} : {message}',
			'style': '{',
		},
		'simple': {
			'format': '[{asctime}] {levelname} : {message}',
			'style': '{',
		},
	},
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse',
		},
		'require_debug_true': {
			'()': 'django.utils.log.RequireDebugTrue',
		},
	},
	'handlers': {
		'console': {
			'level': 'WARNING',
			'filters': ['require_debug_true'],
			'class': 'logging.StreamHandler',
			# 'formatter': 'simple',
		},
		'file': {
			'level': 'WARNING',
			'filters': ['require_debug_false'],
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': make_path('debug.log'),
			'maxBytes': 1024*1024*15,  # 15MB
			'backupCount': 5,
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console', 'file'],
			'level': 'WARNING',
			'propagate': True,
		},
	},
}
