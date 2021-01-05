from . import *


SECRET_KEY = '-~aO;| F;rE[??/w^zcumh(9'
SECRET_KEY_DB = '-~aO;| F;rE[??/w^zcumh(9'

DEBUG = False

ALLOWED_HOSTS = ['178.62.117.192']


DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'site',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '91.160.143.22',
        'PORT': '32770',
    }
}