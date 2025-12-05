import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_booking_system.settings")

# WSGI handler for Vercel
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

