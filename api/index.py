import os
import sys

from django.core.wsgi import get_wsgi_application

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookmyseat.settings")

# Setup WSGI application
application = get_wsgi_application()

# Optional: Serve static files
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(project_root, "staticfiles"))



