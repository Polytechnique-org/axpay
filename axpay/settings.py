"""
Django settings for axpay project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(ROOT_DIR, ...)
import os.path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CHECKOUT_DIR = os.path.abspath(os.path.dirname(ROOT_DIR))

import getconf

config = getconf.ConfigGetter('axpay',
    '/etc/axpay/settings.ini',
    os.path.join(CHECKOUT_DIR, 'local_settings.ini'),
    )

# ENV: The current environment
ENV = config.get('environment', 'dev')
assert ENV in ('dev', 'prod'), "Invalid environment %s" % ENV

# SERVICE: The current service being run
SERVICE = config.get('service', 'core')
assert SERVICE in ('core', 'www'), "Invalid service %s" % SERVICE


# Debug
# =====

DEBUG = (ENV == 'dev' and config.getbool('dev.debug', True))
TEMPLATE_DEBUG = DEBUG

# Applications
# ============

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'bootstrap3',  # For pretty forms too
    'django_authgroupex',
)

CORE_APPS = (
    'axpay.money',
    'axpay.util',
)

WWW_APPS = (
    'axpay.web',
    'axpay.sales',
    'axpay.contributions',
)

DEV_APPS = (
    'debug_toolbar.apps.DebugToolbarConfig',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CORE_APPS + WWW_APPS


# Service-specific settings
# =========================

if SERVICE == 'www':
    ROOT_URLCONF = 'axpay.web.urls'
    TEST_APPS = WWW_APPS
else:
    ROOT_URLCONF = 'axpay.urls'
    TEST_APPS = CORE_APPS

if ENV == 'dev':
    INSTALLED_APPS += DEV_APPS

# Django configuration
# ====================

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': config.get('db.name', os.path.join(CHECKOUT_DIR, 'db.sqlite')),
        'ATOMIC_REQUESTS': True,
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = config.getlist('django.allowed_hosts', '')

AUTHENTICATION_BACKENDS = (
    'django_authgroupex.auth.AuthGroupeXBackend',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# AuthGroupeX settings

AUTHGROUPEX_KEY = config.get('authgroupex.key', '')
AUTHGROUPEX_FIELDS = ('username', 'firstname', 'lastname', 'email', 'promo')
AUTHGROUPEX_USER_MODEL = 'auth.User'
AUTHGROUPEX_RETURN_URL = '/xorgauth/'
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if ENV == 'dev':
    AUTHGROUPEX_FAKE = True
    AUTHGROUPEX_ENDPOINT = 'authgroupex:fake_endpoint'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', 'English'),
    ('fr', 'French'),
)

LOCALE_PATHS = (
    os.path.join(ROOT_DIR, 'locale'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = config.get('django.media_root', os.path.join(CHECKOUT_DIR, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = config.get('django.media_url', '/media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(ROOT_DIR, 'static', SERVICE)

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = config.get('django.static_url', '/static/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
if ENV == 'dev':
    _default_secret_key = 'Dev Only!!'
else:
    _default_secret_key = ''
SECRET_KEY = config.get('django.secret_key', _default_secret_key)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

if ENV == 'dev':
    INTERNAL_IPS = ('127.0.0.1', '::1')

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'axpay.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_DIR, 'web', 'templates'),
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'null': {
            'level': 'ERROR',
            'class': 'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'] if os.environ.get('LOG_TO_STDERR') == '1' else ['null'],
        'level': 'INFO',
    },
}


if config.getbool('dev.jenkins'):
    TEST_RUNNER = 'axpay.util.test.AXPayXMLTestSuiteRunner'
    TEST_OUTPUT_DIR = os.path.join('reports', SERVICE)
    TEST_OUTPUT_VERBOSE = 2
    # Always output description of tests to XML
    TEST_OUTPUT_DESCRIPTIONS = True

else:
    TEST_RUNNER = 'axpay.util.test.AXPayTestSuiteRunner'

# Context processors
# ==================

TEMPLATE_STRING_IF_INVALID = '<InvalidVar %s>'

# Conftools settings
# ==================

CONFTOOLS_CONFIG = config

# Bootstrap3
# ==========

BOOTSTRAP3 = {
    'set_placeholder': False,
}

