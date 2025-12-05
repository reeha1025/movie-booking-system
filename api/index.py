# api/index.py
import os
import sys

# Ensure project root is on sys.path (adjust if your repo layout differs)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookmyseat.settings")

# Optional: reduce logging verbosity in Vercel logs if you want
# import logging
# logging.getLogger("django").setLevel(logging.WARNING)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


