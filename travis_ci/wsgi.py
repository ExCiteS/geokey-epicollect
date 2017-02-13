"""Default WSGI."""

import os

from django.core.wsgi import get_wsgi_application


settings_module = 'settings'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = get_wsgi_application()
