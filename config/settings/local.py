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

# DEBUG_TOOLBAR_CONFIG = {
#     'DISABLE_PANELS': [
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#     ],
#     'SHOW_TEMPLATE_CONTEXT': True,
# }

# INSTALLED_APPS += [
#     ''
# ]
