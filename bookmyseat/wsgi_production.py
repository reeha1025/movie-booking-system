"""
WSGI config for bookmyseat project in production.
It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings_production')

application = get_wsgi_application()
app = application