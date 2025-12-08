from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from movies.views import analytics_dashboard

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

