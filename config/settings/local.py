import os
import socket

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-fh0qrcyl)%ln8+q4pu_s-ao5n#zc+adfpd0wtvi0bpwp!0nc5i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1']

# INSTALLED_APPS += [
#     ''
# ]

DATABASE_URL = f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
REDIS_URL = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"

CELERY_BROKER_URL = f"{REDIS_URL}/0"

CELERY_RESULT_BACKEND = CELERY_BROKER_URL

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('POSTGRES_DB'),
        "USER": os.getenv('POSTGRES_USER'),
        "PASSWORD": os.getenv('POSTGRES_PASSWORD'),
        "HOST": os.getenv('POSTGRES_HOST'),
        "PORT": os.getenv('POSTGRES_PORT'),
    }
}