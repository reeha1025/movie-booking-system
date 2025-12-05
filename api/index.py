from pathlib import Path
import sys
import os

# Add your project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Set DJANGO_SETTINGS_MODULE correctly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookmyseat.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

