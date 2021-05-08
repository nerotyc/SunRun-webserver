
import os
from pathlib import Path

from dotenv import load_dotenv

sep = os.path.sep
DOT_ENV_STRING = str(str(Path(__file__).resolve().parent.parent.parent.parent) + f"{sep}.config{sep}.django.env")
load_dotenv(DOT_ENV_STRING)

from django.core.exceptions import ImproperlyConfigured

def get_env_value(env_variable):
    try:
      	return os.environ.get(env_variable)
    except KeyError:
        error_msg = 'Set the {} environment variable'.format(var_name)
        raise ImproperlyConfigured(error_msg)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_value('SECRET_KEY')

DEBUG = get_env_value('DEBUG')

DB_LOCAL = True  # whether to use home mysql etc. or production
PRODUCTION_STATIC_DIRS = False

SECURE_SSL_REDIRECT = False

ALLOWED_HOSTS = [
    "run.djk-sonnen.de",
    "127.0.0.1",
    "localhost",
    "192.168.178.70",
    "192.168.178.31",
    "djk-sonnen.de"]


# Application definition

INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'rest_framework.authtoken',
    'crispy_forms',
    'multiselectfield',
    'timedeltatemplatefilter',

    # own apps
    'dashboard.apps.DashboardConfig',
    'route.apps.RouteConfig',
    'user.apps.UserConfig',
    'run.apps.RunConfig',
    'strava_run.apps.StravaRunConfig',
    'api.apps.ApiConfig',
    'group.apps.GroupConfig',

]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# for routing
ROOT_URLCONF = 'sonnen_rennt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'define_action': 'sonnen_rennt.templatetags.define_action',

            }
        },
    },
]

WSGI_APPLICATION = 'sonnen_rennt.wsgi.application'

DB_HOST= get_env_value('DATABASE_HOST')
DB_NAME= get_env_value('DATABASE_NAME')
DB_PORT= str(get_env_value('DATABASE_PORT'))
DB_USER= get_env_value('DATABASE_USER')
DB_PASSWORD= get_env_value('DATABASE_PASSWORD')

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '3307',
        'OPTIONS': {'charset': 'utf8mb4'},
        # 'OPTIONS': {
        #     'read_default_file': '/sql_db.cnf',
        # },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


if not PRODUCTION_STATIC_DIRS:
    # Add these new lines
    STATICFILES_DIRS = (
        #     os.path.join(BASE_DIR, 'static/'),
        os.path.join(BASE_DIR, 'templates'),
    )
    STATIC_URL = '/static/'
    # STATIC_ROOT = os.path.join(BASE_DIR, 'templates/')

else:  # PRODUCTION
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'templates')
    print("STATIC_ROOT: ", STATIC_ROOT)


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/user/login/'


# SMTP Configuration

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.strato.de'  # 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'noreply@djk-sonnen.de'
# EMAIL_HOST_PASSWORD = ''
#
# SERVER_EMAIL = 'noreply@djk-sonnen.de'
