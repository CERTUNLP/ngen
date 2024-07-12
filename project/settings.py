"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import shutil
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _, gettext_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#j!42e(tj8h#n&nl#cxg#(lu=j9=(pcf*=tep$qv%@1^yst4!*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() in ('true', '1', 't')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'constance',
    'constance.backends.database',
    "corsheaders",
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework.authtoken',
    'ngen.apps.NgenConfig',
    'django.contrib.postgres',
    'netfields',
    'django_filters',
    'treebeard',
    'djcelery_email',
    'django_celery_beat',
    'django_bleach',
    'django_extensions',
    'debug_toolbar',
    'auditlog',
    'colorfield',
    'comment',
    'drf_spectacular',
    'generic_relations',
    # django_elasticsearch_dsl added later
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'ngen.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        # 'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.AdminRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'ngen.pagination.CustomPagination',
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ),
    'EXCEPTION_HANDLER': 'ngen.exceptions.django_error_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en-us', _('English')),
    ('es', _('Spanish')),
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'ngen/locale'),
)
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/api/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIA_URL = '/api/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_TASK_SERIALIZER = 'json'

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# CELERY_EMAIL_BACKEND
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
CELERY_BEAT_SCHEDULE = {
    "attend_cases": {
        "task": "ngen.tasks.attend_cases",
        "schedule": crontab(minute="*/1"),
    },
    "solve_cases": {
        "task": "ngen.tasks.solve_cases",
        "schedule": crontab(minute="*/1"),
    },
}

CONSTANCE_BACKEND = 'constance.backends.redisd.CachingRedisBackend'
CONSTANCE_REDIS_CONNECTION = os.environ.get('CONSTANCE_REDIS_CONNECTION', 'redis://ngen-redis:6379/1')
CONSTANCE_REDIS_CACHE_TIMEOUT = int(os.environ.get('CONSTANCE_REDIS_CACHE_TIMEOUT', 60))
CONSTANCE_FILE_ROOT = 'config'
CONSTANCE_ADDITIONAL_FIELDS = {
    'image_field': ['django.forms.ImageField', {}],
    'priority_field': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (
            ('Critical', gettext_lazy('Critical')), ('High', gettext_lazy('High')),
            ('Medium', gettext_lazy('Medium')), ('Low', gettext_lazy('Low')),
            ('Very low', gettext_lazy('Very low'))),
    }],
    'case_lifecycle': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (
            ('manual', gettext_lazy('Manual')), ('auto', gettext_lazy('Auto')), (
                'auto_open', gettext_lazy('Auto open')), ('auto_close', gettext_lazy('Auto close')))
    }],
    'allowed_artifacts': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (
            ('ip', 'IP'), ('domain', gettext_lazy('Domain')), (
                'url', 'Url'), ('hash', 'Hash'), ('file', gettext_lazy('File')), ('domain', gettext_lazy('Domain'))),
    }],
}
CONSTANCE_CONFIG = {
    'TEAM_EMAIL': (os.environ.get('TEAM_EMAIL'), 'CSIRT team email'),
    'TEAM_EMAIL_PRIORITY': (os.environ.get('TEAM_EMAIL_PRIORITY'), 'CSIRT team email', 'priority_field'),
    'TEAM_ABUSE': (os.environ.get('TEAM_ABUSE'), 'CSIRT abuse email'),
    'TEAM_URL': (os.environ.get('TEAM_URL'), 'CSIRT site url'),
    'TEAM_SITE': (os.environ.get('TEAM_SITE'), 'CSIRT team site'),
    'TEAM_LOGO': (os.path.join(CONSTANCE_FILE_ROOT, 'teamlogo.png'),
                  f'Team logo will be saved at /api/media/{CONSTANCE_FILE_ROOT}/teamlogo.png and generated image of 200x50 pixels max for email logo at /api/media/{CONSTANCE_FILE_ROOT}/teamlogo_200_50.png',
                  'image_field'),
    'TEAM_NAME': (os.environ.get('TEAM_NAME'), 'CSIRT name'),
    'EMAIL_SENDER': (os.environ.get('EMAIL_SENDER'), 'SMTP sender email address'),
    'NGEN_LANG': (os.environ.get('NGEN_LANG'), 'NGEN default language'),
    'NGEN_LANG_EXTERNAL': (os.environ.get('NGEN_LANG_EXTERNAL'), 'NGEN language for external reports'),
    'ALLOWED_FIELDS_MERGED_CASE': (os.environ.get('ALLOWED_FIELDS_MERGED_CASE'),
                            'Case comma separated fields that could be modified if the instance is blocked'),
    'ALLOWED_FIELDS_MERGED_EVENT': (os.environ.get('ALLOWED_FIELDS_MERGED_EVENT'),
                             'Event comma separated fields that could be modified if the instance is blocked. '),
    'ALLOWED_FIELDS_BLOCKED_CASE': (os.environ.get('ALLOWED_FIELDS_BLOCKED_CASE'),
                            'Case comma separated fields that could be modified if the instance is blocked'),
    'ALLOWED_FIELDS_BLOCKED_EVENT': (os.environ.get('ALLOWED_FIELDS_BLOCKED_EVENT'),
                             'Event comma separated fields that could be modified if the instance is blocked. '),
    'ALLOWED_FIELDS_BLOCKED_EXCEPTION': (os.environ.get('ALLOWED_FIELDS_BLOCKED_EXCEPTION', 'false').lower() in ('true', '1', 't'),
                                 'If True, ngen will raise an exception if a blocked field is modified', bool),
    'PRIORITY_ATTEND_TIME_DEFAULT': (
        int(os.environ.get('PRIORITY_ATTEND_TIME_DEFAULT', 10080)), 'Priority default attend time in minutes', int),
    'PRIORITY_SOLVE_TIME_DEFAULT': (
        int(os.environ.get('PRIORITY_SOLVE_TIME_DEFAULT', 10080)), 'Priority default solve time in minutes', int),
    'CASE_DEFAULT_LIFECYCLE': (
        os.environ.get('CASE_DEFAULT_LIFECYCLE', 'manual'), 'Case default lifecycle', 'case_lifecycle'),
    'CASE_REPORT_NEW_CASES': (
        os.environ.get('CASE_REPORT_NEW_CASES', 'false').lower() in ('true', '1', 't'),
        'Send report on new cases.', bool),
    'PRIORITY_DEFAULT': (os.environ.get('PRIORITY_DEFAULT', 'Medium'), 'Default priority', 'priority_field'),
    'ALLOWED_ARTIFACTS_TYPES': (os.environ.get('ALLOWED_ARTIFACTS_TYPES'), 'Allowed artifact types'),
    'ARTIFACT_SAVE_ENRICHMENT_FAILURE': (
        os.environ.get('ARTIFACT_SAVE_ENRICHMENT_FAILURE', 'false').lower() in ('true', '1', 't'),
        'Save enrichment even if it fails.', bool),
    'ARTIFACT_RECURSIVE_ENRICHMENT': (
        os.environ.get('ARTIFACT_RECURSIVE_ENRICHMENT', 'false').lower() in ('true', '1', 't'),
        'Enrich artifacts from artifacts enrichmets', bool),
    'CORTEX_HOST': (os.environ.get('CORTEX_HOST'), 'Cortex host domain:port'),
    'CORTEX_APIKEY': (os.environ.get('CORTEX_APIKEY', ''), 'Cortex admin apikey'),
    'PAGE_SIZE': (int(os.environ.get('PAGE_SIZE', 10)), 'Default page size', int),
    'PAGE_SIZE_MAX': (int(os.environ.get('PAGE_SIZE_MAX', 100)), 'Max page size (use with caution)', int),
}
CONSTANCE_CONFIG_PASSWORDS = ['CORTEX_APIKEY']

os.makedirs(os.path.join(MEDIA_ROOT, CONSTANCE_FILE_ROOT), exist_ok=True)
LOGO_PATH = os.path.join(f'{MEDIA_ROOT}', CONSTANCE_CONFIG['TEAM_LOGO'][0])
origin_path = os.path.join(f'{STATIC_ROOT}', 'img', 'teamlogo.png')
if not os.path.exists(LOGO_PATH) and os.path.exists(origin_path):
    shutil.copy(origin_path, LOGO_PATH)

LOGO_WIDE_SIZE = (200, 50)
LOGO_WIDE_PATH = os.path.join(f'{MEDIA_ROOT}', CONSTANCE_FILE_ROOT, 'teamlogo_200_50.png')
origin_path = os.path.join(f'{STATIC_ROOT}', 'img', 'teamlogo_200_50.png')
if not os.path.exists(LOGO_WIDE_PATH) and os.path.exists(origin_path):
    shutil.copy(origin_path, LOGO_WIDE_PATH)

AUTH_USER_MODEL = 'ngen.User'

BLEACH_ALLOWED_TAGS = ['p', 'b', 'i', 'u', 'strong', 'a', 'ul', 'li', 'div', 'br']
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style']
# Which CSS properties are allowed in 'style' attributes (assuming style is an allowed attribute)
BLEACH_ALLOWED_STYLES = [
    'font-family', 'font-weight', 'text-decoration', 'font-variant']
# Strip unknown tags if True, replace with HTML escaped characters if False
BLEACH_STRIP_TAGS = True
# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = False

if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    DEBUG_INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips]
    DEBUG_INTERNAL_IPS += os.environ.get('DJANGO_DEBUG_INTERNAL_IPS', '').split(',')

    # Toolbar settings
    def show_toolbar(request):
        if not DEBUG:
            return False

        # Do not show toolbar if the request is AJAX
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return False

        # Show toolbar if the IP in HTTP_X_REAL_IP or REMOTE_ADDR is in DEBUG_INTERNAL_IPS
        if (request.META.get('HTTP_X_REAL_IP', None) in DEBUG_INTERNAL_IPS or
                request.META.get('REMOTE_ADDR', None) in DEBUG_INTERNAL_IPS):
            return True

        return False

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    }

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.environ.get('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')

COMMENT_ALLOW_SUBSCRIPTION = True
COMMENT_ALLOW_TRANSLATION = True

ELASTIC_ENABLED = os.environ.get('ELASTIC_ENABLED', 'false').lower() in ('true', '1', 't')
if ELASTIC_ENABLED:
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': f"{os.environ.get('ELASTIC_HOST')}:{os.environ.get('ELASTIC_PORT')}"
        },
    }
    INSTALLED_APPS += ['django_elasticsearch_dsl', 'django_elasticsearch_dsl_drf']

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=15),
    "ROTATE_REFRESH_TOKENS": True,
    # Blacklist refresh tokens could be a logging problem on refresh token rotation if they are parallel requests
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,  # check if this is needed and performance impact

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
