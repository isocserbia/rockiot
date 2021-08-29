"""
Django settings for rockiot project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+kw3hg326l#06$3c6_dmahite83n6+d3ey-a2kaqhvl!&+(9u6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['localhost', '0.0.0.0', 'rockiot', 'rabbit', 'http://0.0.0.0:8000']
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'app',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.gis",
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django_admin_row_actions',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_simplejwt',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
    'PAGE_SIZE': 100
}

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries' : {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'
GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so'
GEOS_LIBRARY_PATH = '/usr/lib/libgeos_c.so'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('TS_DB', default='rock_iot'),
        'USER': config('TS_USER', default='postgres'),
        'PASSWORD': config('TS_PASS', default='postgres'),
        'HOST': config('TS_HOST', default='localhost'),
        'PORT': config('TS_PORT', default='5432'),
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

BROKER_CONFIG = {
    'RABBITMNGMT_USER': config('RABBITMNGMT_USER', default='rabbitmngmt'),
    'RABBITMNGMT_PASS': config('RABBITMNGMT_PASS', default='rabbitmngmt_pass'),
    'AMQPTASKPRODUCER_USER': config('AMQPTASKPRODUCER_USER', default='amqptaskproducer'),
    'AMQPTASKPRODUCER_PASS': config('AMQPTASKPRODUCER_PASS', default='amqptaskproducer_pass'),
    'AMQPTASKCONSUMER_USER': config('AMQPTASKCONSUMER_USER', default='amqptaskconsumer'),
    'AMQPTASKCONSUMER_PASS': config('AMQPTASKCONSUMER_PASS', default='amqptaskconsumer_pass'),
    'MQTTEVENTPRODUCER_USER': config('MQTTEVENTPRODUCER_USER', default='mqtteventproducer'),
    'MQTTEVENTPRODUCER_PASS': config('MQTTEVENTPRODUCER_PASS', default='mqtteventproducer_pass'),
    'BROKER_HOST': config('BROKER_HOST', default='localhost'),
    'BROKER_VHOST': config('BROKER_VHOST', default='/'),
    'BROKER_AMQP_PORT': config('BROKER_AMQP_PORT', default='5672'),
    'BROKER_AMQP_SSL_PORT': config('BROKER_AMQP_SSL_PORT', default='5671'),
    'BROKER_MQTT_PORT': config('BROKER_MQTT_PORT', default='1883'),
    'BROKER_MQTT_SSL_PORT': config('BROKER_MQTT_SSL_PORT', default='8883'),
    'BROKER_MNGMT_PORT': config('BROKER_MNGMT_PORT', default='15672'),
    'BROKER_MNGMT_SSL_PORT': config('BROKER_MNGMT_SSL_PORT', default='15673'),
    'BROKER_EXCHANGE': config('BROKER_EXCHANGE', default='amq.topic'),
    'BROKER_TASK_QUEUE': config('BROKER_TASK_QUEUE', default='tasks_amqp'),
    'BROKER_DELAYED_TASK_QUEUE': config('BROKER_DELAYED_TASK_QUEUE', default='tasks_amqp_delay'),
    'BROKER_ATTRIBUTES_TOPIC': config("BROKER_ATTRIBUTES_TOPIC", default='v1.attributes'),
    'BROKER_DEVICE_EVENTS_TOPIC': config("BROKER_DEVICE_EVENTS_TOPIC", default='v1.devices.%s.events'),
    'BROKER_DEVICE_ACTIONS_TOPIC': config("BROKER_DEVICE_ACTIONS_TOPIC", default='v1.devices.actions'),
    'BROKER_DEVICE_INGEST_TOPIC': config("BROKER_DEVICE_INGEST_TOPIC", default='v1.devices.%s.actions.ingest')
}

ROCKIOT_CONFIG = {
    'FAULT_DIFF_PERC_TEMPERATURE': int(config('FAULT_DIFF_PERC_TEMPERATURE', default='100')),
    'FAULT_DIFF_PERC_HUMIDITY': int(config('FAULT_DIFF_PERC_HUMIDITY', default='100')),
    'FAULT_DIFF_PERC_SMOKE': int(config('FAULT_DIFF_PERC_SMOKE', default='100')),
    'FAULT_DIFF_PERC_CO': int(config('FAULT_DIFF_PERC_CO', default='100')),
    'FAULT_SECONDS_SINCE_LAST_ENTRY': int(config('FAULT_SECONDS_SINCE_LAST_ENTRY', default='300')),
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(name)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'pyrabbit2': {
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    }
}

# if DEBUG:
#     # make all loggers use the console.
#     for logger in LOGGING['loggers']:
#         LOGGING['loggers'][logger]['handlers'] = ['console']
