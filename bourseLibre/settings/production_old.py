from . import *


SECRET_KEY = '*(&5tv0&)&2$nfirrc7yh1@nuwesj2hc*myl13k#)v#2b4fl2!'
EMAIL_ADMIN_PWD = 'permaiole66!'
GAPI_KEY = 'AIzaSyCmGcPj0ti_7aEagETrbJyHPbE3U6gVfSA'

DEBUG = False

ALLOWED_HOSTS = ['82.64.236.35','127.0.0.1']


DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'site',
        'USER': 'postgres',
        'PASSWORD': 'AssociAtionPermAcultureCAtAlAne',
        'HOST': '82.64.236.35',
        'PORT': '32770',
    }
}
