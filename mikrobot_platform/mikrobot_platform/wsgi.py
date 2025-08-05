"""
WSGI config for Mikrobot Trading Platform.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_platform.settings')

application = get_wsgi_application()