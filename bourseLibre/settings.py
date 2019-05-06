# -*- coding: utf-8 -*-
"""
Django settings for bourseLibre project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/

 python manage.py createsuperuser
python manage.py migrate --run-syncdb

"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

try:
    import dj_database_url
except:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
LOCALL = False
try:
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = False
except:
    LOCALL  = True
    SECRET_KEY = 'aersd68fgsfdgsdvcbvcb563873gbgfthhfhdjd'
    DEBUG = True

#DEBUG_PROPAGATE_EXCEPTIONS = True

#SECURE_SSL_REDIRECT = False
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE=True


ALLOWED_HOSTS = ['permacat.herokuapp.com', 'www.perma.cat']

# Application definition

# pip install django-fontawesome django-model_utils django-debug_toolbar django-haystack django-bootstrap django-extensions django-leaflet django-filter django-rest-framework django-scheduler django-widget-tweaks

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.sites',
    #'django.contrib.gis',
    'bootstrap','fontawesome','cookielaw',
    #'haystack',
    #'debug_toolbar',
    'model_utils',
    #'address',
    'bourseLibre',
    'blog',
    'django_extensions',
    'django_filters',
    'rest_framework',
    'schedule','djangobower',
    'widget_tweaks',
    'leaflet',
    #'tinymce',
    'captcha',
    'django_summernote',
    'actstream',
    #'notifications',
    #'webpush',
    #"geoposition",
    #"geodjango",
    #'osm_field',
    #'location_field.apps.DefaultConfig',
    #'sitetree',
    #'panier',
    #'location-field',
    #'polymorphic',  # We need polymorphic installed for the shop
    #'shop',  # The django SHOP application
    #'shop.addressmodel',  # The default Address and country models
    # 'regist#ration'
)

# MIDDLEWARE_CLASSES = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.common.BrokenLinkEmailsMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
# )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'django.middleware.locale.LocaleMiddleware',
   # 'bourseLibre.middleware.SetLastVisitMiddleware'
    #'django.core.context_processors.request',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]


ROOT_URLCONF = 'bourseLibre.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
            'string_if_invalid': 'Invalid: "%s"',
            'libraries': {'is_numeric': 'bourseLibre.templatetags.app_filters', }
        },
    },
]

WSGI_APPLICATION = 'bourseLibre.wsgi.application'
# Database
if LOCALL:
    DATABASES = {
       'default': {
          'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.db'),
        }
    }
    ALLOWED_HOSTS = ['127.0.0.1']
else:
    DATABASES = dict()
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)


# except:


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    #{    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    #{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    #{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
#         'URL': 'http://127.0.0.1:8000/',
#         'INDEX_NAME': 'haystack',
#     },
# }y
#HAYSTACK_CONNECTIONS = {
#    'default': {
#        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
#        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
#    },
#}
HAYSTACK_CONNECTIONS = {
  'default': {
    'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
    'PATH': os.path.join(os.path.dirname(__file__), 'search_index'),
  },
}
AUTH_USER_MODEL = 'bourseLibre.Profil'
# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

SITE_ID = 1

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = "l d F Y"
DATE_FORMAT_COURT = "d F Y"
DATE_FORMAT_COURT_HEURE = "d F Y, G:i"
#DATETIME_INPUT_FORMATS = '%d/%m/%Y'
#TIME_INPUT_FORMATS = '%H:%M'
SHORT_DATE_FORMAT = "d F Y"
#DATE_INPUT_FORMATS = ('%d/%m/%Y',)


LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

INTERNAL_IPS = ['127.0.0.1']

########################
import re
IGNORABLE_404_URLS = (
    re.compile('\.(php|cgi)$'),
    re.compile('^/phpmyadmin/'),
    re.compile('^/apple-touch-icon.*\.png$'),
    re.compile('^/favicon\.ico$'),
    re.compile('^/robots\.txt$'),
)

# Email settings
SERVER_EMAIL = 'sitepermacat@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
try:
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_ADMIN_PWD']
except:
    EMAIL_HOST_PASSWORD = 'gg'
EMAIL_HOST_USER = SERVER_EMAIL
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
GMAIL_SMTP_USER = 'sitepermacat@gmail.com'
EMAIL_SUBJECT_PREFIX = "[PermaCat]"
try:
    GMAIL_SMTP_PASSWORD = os.environ['EMAIL_ADMIN_PWD']
except:
    GMAIL_SMTP_PASSWORD = 'test'

ADMINS = (
    ('Asso_admin', 'sitepermacat@gmail.com'),
)
MANAGERS = ADMINS
BASE_URL = "https://permacat.herokuapp.com"
########################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
#STATICFILES_DIRS = (os.path.join(BASE_DIR, 'staticfiles'), )

MEDIA_URL = '/static/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media/')


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# LOCATION_FIELD = {
#     'map.provider': 'openstreetmap',
# }


LEAFLET_CONFIG = {
'DEFAULT_CENTER': (42.7201813, 2.8876436),
'DEFAULT_ZOOM': 10,
'MIN_ZOOM': 3,
'MAX_ZOOM': 18,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

PHONENUMBER_DEFAULT_REGION = 'EUROPE'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

gettext =  lambda x: x
LANGUAGES = (
   ('fr', gettext('French')),
   ('ca', gettext('Catalan')),
)

SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode, default
    'iframe': True,

    # Or, you can set it as False to use SummernoteInplaceWidget by default - no iframe mode
    # In this case, you have to load Bootstrap/jQuery stuff by manually.
    # Use this when you're already using Bootstraip/jQuery based themes.
    #'iframe': False,

    # You can put custom Summernote settings
    'summernote': {

        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': 'fr-FR',
},
"toolbar": [
    ['style', ['bold', 'italic', 'underline', 'clear']],
    ['fontsize', ['fontsize']],
    ['fontSizes', ['8', '9', '10', '11', '12', '14', '18', '22', '24', '36']],
    ['color', ['color']],
    ['para', ['ul', 'ol', 'paragraph']],
    ['link', ['link', 'picture', 'video', 'table', 'hr',]],
    ['misc', [ 'undo', 'redo', 'help','fullscreen', 'codeview',  'readmore']],

],
"popover": {
  "image": [
    ['imagesize', ['imageSize100', 'imageSize50', 'imageSize25']],
    ['float', ['floatLeft', 'floatRight', 'floatNone']],
    ['remove', ['removeMedia']]
  ],
  "link": [
    ['link', ['linkDialogShow', 'unlink']]
  ],
  "air": [
    ['color', ['color']],
    ['font', ['bold', 'underline', 'clear']],
    ['para', ['ul', 'paragraph']],
    ['table', ['table']],
    ['insert', ['link', 'picture']]
  ]
},


# Need authentication while uploading attachments.
'attachment_require_authentication': True,

# You can disable attachment feature.
'disable_attachment': True,

# Set `True` to return attachment paths in absolute URIs.
'attachment_absolute_uri': False,

# You can add custom css/js for SummernoteWidget.
'css': (
),
'js': (
),

# You can also add custom css/js for SummernoteInplaceWidget.
# !!! Be sure to put {{ form.media }} in template before initiate summernote.
'css_for_inplace': (
),
'js_for_inplace': (
),

# Codemirror as codeview
# If any codemirror settings are defined, it will include codemirror files automatically.
'css': (
    '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/monokai.min.css',
),
'codemirror': {
    'mode': 'htmlmixed',
    'lineNumbers': 'true',

    # You have to include theme file in 'css' or 'css_for_inplace' before using it.
    'theme': 'monokai',
},

# Lazy initialize
# If you want to initialize summernote at the bottom of page, set this as True
# and call `initSummernote()` on your page.
'lazy': True,

# To use external plugins,
# Include them within `css` and `js`.
#'js': {
#},
}

# WEBPUSH_SETTINGS = {
#     "VAPID_PUBLIC_KEY": "BLyCoFZY_vO7P7xHVJg27iqbDaLhfRQfg_sKbE1kx4NBZ1zLEgXy8VWUYn3yFbUQoPte99fUnH8KV-2wt-cZlk0",
#     "VAPID_PRIVATE_KEY":"P26Rpbr7yJT6fNBbgo8H_7t0ueiQFsoyl9RsJvqIYyE",
#     "VAPID_ADMIN_EMAIL": "sitepermacat@gmail.com"
# }

ACTSTREAM_SETTINGS = {
    #'MANAGER': 'myapp.managers.MyActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 1,
}
