from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movies.views import analytics_dashboard
urlpatterns = [
    path('secure-admin-panel-bms2025/', admin.site.urls),
    path('users/', include('users.urls')),
    path('',include('users.urls')),
    path('movies/', include('movies.urls')),
    path('secure-analytics-bms2025/', analytics_dashboard, name='analytics_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("movies.urls")),   # ADD THIS
]

