"""
Django settings for cs_cas project.

Environment-specific values and secrets are read from environment variables. In local development they are loaded
from the `.env` file at the project root (copy `.env.example` to `.env`). Real environment variables take precedence
over values in `.env`.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""
from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


# Core settings
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

SECRET_KEY = env.str('DJANGO_SECRET_KEY')

DEBUG = env.bool('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

TWO_FACTOR_PATCH_ADMIN = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Third-party apps
    'pgtrigger',
    'phonenumber_field',
    'ninja_jwt',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'two_factor.plugins.phonenumber',
    
    # Local apps
    'common',
    'myadmin',
    'myauth',
    'catalogs',
    'ships_cabins',
    'routes',
    'seasons_sailings',
    'pricing',
    'discounts',
    'selling',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cs_cas.urls'

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

WSGI_APPLICATION = 'cs_cas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST', default='localhost'),
        'PORT': env.int('POSTGRES_PORT', default=5432),
        'OPTIONS': {
            'connect_timeout': 5,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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

# Use Argon2 as the default storage algorithm for passwords
# https://docs.djangoproject.com/en/6.1/topics/auth/passwords/
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_USER_MODEL = 'myauth.User'

# Two-Factor Authentication (SMS) and email delivery. The defaults print messages to the console; set real
# backends per environment.
TWO_FACTOR_SMS_GATEWAY = env.str('TWO_FACTOR_SMS_GATEWAY', default='two_factor.gateways.fake.Fake')
MAILERS = {
    "default": {
        "BACKEND": env.str('EMAIL_BACKEND', default="django.core.mail.backends.console.EmailBackend"),
    },
}

# Logging settings for debugging purposes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

# JWT environment var settings
NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),

    # aud/iss claims
    'AUDIENCE': 'cscas-client',
    'ISSUER': 'cscas-api',

    # algorithm choice
    # keep default for now, switch to RS256 later
    # 'ALGORITHM': 'RS256',
    # 'SIGNING_KEY':
    # 'VERIFYING_KEY':

    # clock skew
    'LEEWAY': 60, # seconds (±60s)
}

REFRESH_COOKIE_KEY = 'cscas-refresh'
REFRESH_IDLE_TIMEOUT = timedelta(days=7)

# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/6.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str('REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Object Storage (S3-compatible: Silo locally, AWS S3 or similar in production)
S3_ENDPOINT_URL = env.str('S3_ENDPOINT_URL')
S3_ACCESS_KEY = env.str('S3_ACCESS_KEY')
S3_SECRET_KEY = env.str('S3_SECRET_KEY')
S3_BUCKET_NAME = env.str('S3_BUCKET_NAME')
S3_PUBLIC_URL = env.str('S3_PUBLIC_URL')  # base URL for public file access

# External integrations
GOOGLE_PLACES_API_KEY = env.str('GOOGLE_PLACES_API_KEY', default='')
