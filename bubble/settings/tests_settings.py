from . import *

DEBUG = os.getenv("DEBUG_PROD")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "test_bubble",
        'USER': "test_bubble_user",
        'PASSWORD': "test_bubble_password",
        'HOST': "localhost",
        'PORT': '',
    }
}