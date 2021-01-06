from . import *


SECRET_KEY = '-~aO;| F;rE[??/w^zcumh(9'
SECRET_KEY_DB = '-~aO;| F;rE[??/w^zcumh(9'

DEBUG = False

ALLOWED_HOSTS = ['']


DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'site',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}