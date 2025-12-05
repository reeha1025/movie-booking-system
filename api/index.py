# api/index.py
import os
import sys
from django.core.wsgi import get_wsgi_application

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookmyseat.settings")

# WSGI app
application = get_wsgi_application()

# Serve static files
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.dirname(__file__)), "staticfiles"))




