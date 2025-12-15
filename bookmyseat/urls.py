from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

# Import analytics view defensively so a broken movies.views import won't break startup
try:
    from movies.views import analytics_dashboard
except Exception as e:
    # Import failure — log for debugging and use a lightweight fallback view
    import logging
    from django.shortcuts import redirect

    logging.exception("Failed to import analytics_dashboard from movies.views: %s", e)

    def analytics_dashboard(request):
        # Simple fallback: redirect to home so site doesn't 500 during deploy.
        return redirect('movie_list')


urlpatterns = [
    # Admin
    path('secure-admin-panel-bms2025/', admin.site.urls),

    # Users app
    path('users/', include('users.urls')),

    # Movies app (Homepage)
    path('', include('movies.urls')),   # 👈 THIS FIXES YOUR 404

    # Analytics
    path('secure-analytics-bms2025/', analytics_dashboard, name='analytics_dashboard'),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
