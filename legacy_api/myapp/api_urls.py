from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .api_views import (
    BookingViewSet,
    CityViewSet,
    MovieViewSet,
    ShowViewSet,
    VenueViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'shows', ShowViewSet, basename='show')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
