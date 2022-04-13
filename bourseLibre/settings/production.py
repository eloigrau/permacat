from . import *


SECRET_KEY = '-~aO;| F;rE[??/w^zcumh(9'
SECRET_KEY_DB = '-~aO;| F;rE[??/w^zcumh(9'
GAPI_KEY = 'zzz'
DB_PWD = 'aaa'

DEBUG = True

ALLOWED_HOSTS = ['']


DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SERVER_EMAIL = 'xxx'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'xxx'
EMAIL_HOST_USER = SERVER_EMAIL
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
GMAIL_SMTP_USER = 'xxx'
EMAIL_SUBJECT_PREFIX = "[xxx]"
GMAIL_SMTP_PASSWORD = 'xxx'

PERMAGORA_USER_MAIL = ""
PERMAGORA_PWD_MAIL = ""

ACME_CHALLENGE_URL_SLUG = ''
ACME_CHALLENGE_TEMPLATE_CONTENT = ''

