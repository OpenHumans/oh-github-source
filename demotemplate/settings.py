"""
Django settings for oh-github-source project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import django_heroku
from env_tools import apply_env
from requests_respectful import RespectfulRequester
# import logging

# logger = logging.getLogger(__name__)

apply_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'ab74b6762803592961bb02a10fd509e53531de9332102784af2e725a8c3fc350')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if os.getenv('DEBUG', '').lower() == 'false' else True

REMOTE = True if os.getenv('REMOTE', '').lower() == 'true' else False

ALLOWED_HOSTS = ['*']

# Check if running on Heroku. If so, force SSL.
ON_HEROKU = os.getenv('ON_HEROKU', 'false').lower() == 'true'
if ON_HEROKU:
    SECURE_SSL_REDIRECT = True

HEROKUCONFIG_APP_NAME = os.getenv('HEROKUCONFIG_APP_NAME', '')

DEFAULT_BASE_URL = ('https://{}.herokuapp.com'.format(HEROKUCONFIG_APP_NAME) if
                    REMOTE else 'http://127.0.0.1:5000')

OPENHUMANS_APP_BASE_URL = os.getenv('APP_BASE_URL', DEFAULT_BASE_URL)
if OPENHUMANS_APP_BASE_URL[-1] == "/":
    OPENHUMANS_APP_BASE_URL = OPENHUMANS_APP_BASE_URL[:-1]

# Open Humans configuration
LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/'
OPENHUMANS_CLIENT_ID = os.getenv('OH_CLIENT_ID')
OPENHUMANS_CLIENT_SECRET = os.getenv('OH_CLIENT_SECRET')
OH_ACTIVITY_PAGE = os.getenv('OH_ACTIVITY_PAGE')
OPENHUMANS_OH_BASE_URL = 'https://www.openhumans.org'

OH_API_BASE = OPENHUMANS_OH_BASE_URL + '/api/direct-sharing'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'
OH_DELETE_FILES = OH_API_BASE + '/project/files/delete/'

#Fitbit Configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI')

# Requests Respectful (rate limiting, waiting)
if REMOTE is True:
    from urllib.parse import urlparse
    url_object = urlparse(os.getenv('REDIS_URL', 'redis://'))
    # logger.info('Connecting to redis at %s:%s',
    #     url_object.hostname,
    #     url_object.port)
    RespectfulRequester.configure(
        redis={
            "host": url_object.hostname,
            "port": url_object.port,
            "password": url_object.password,
            "database": 0
        },
        safety_threshold=5)

# This creates a Realm called "github" that allows 150 requests per minute maximum.
rr = RespectfulRequester()
rr.register_realm("github", max_requests=5000, timespan=3600)

# Applications installed
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps. Update these if you add or change app names!
    'openhumans',
    'datauploader.apps.DatauploaderConfig',
    'main.apps.MainConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'demotemplate.urls'

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

WSGI_APPLICATION = 'demotemplate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# https://devcenter.heroku.com/articles/django-app-configuration


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'UserAttributeSimilarityValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'MinimumLengthValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'CommonPasswordValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'NumericPasswordValidator'),
    },
]

# Configure logging to print Django logs to the console.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

django_heroku.settings(locals())
