import os
from django.core.wsgi import get_wsgi_application
from vercel_wsgi import handle_wsgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_booking_system.settings")

application = get_wsgi_application()

def handler(event, context):
    return handle_wsgi(application, event, context)
