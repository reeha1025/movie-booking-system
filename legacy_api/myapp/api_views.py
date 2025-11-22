from django.utils.dateparse import parse_date
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking, City, Movie, Show, Venue
from .serializers import (
    BookingSerializer,
    CitySerializer,
    MovieSerializer,
    ShowSerializer,
    VenueSerializer,
)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = "slug"


class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VenueSerializer
    queryset = Venue.objects.select_related("city").all()

    def get_queryset(self):
        queryset = super().get_queryset()
        city_slug = self.request.query_params.get("city")
        if city_slug:
            queryset = queryset.filter(city__slug=city_slug)
        return queryset


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class ShowViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShowSerializer

    def get_queryset(self):
        queryset = (
            Show.objects.select_related("movie", "venue", "venue__city")
            .filter(is_active=True)
            .order_by("show_time")
        )
        movie_id = self.request.query_params.get("movie")
        city_slug = self.request.query_params.get("city")
        venue_id = self.request.query_params.get("venue")
        date_param = self.request.query_params.get("date")

        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        if city_slug:
            queryset = queryset.filter(venue__city__slug=city_slug)
        if venue_id:
            queryset = queryset.filter(venue_id=venue_id)
        if date_param:
            parsed_date = parse_date(date_param)
            if parsed_date:
                queryset = queryset.filter(show_time__date=parsed_date)
        return queryset


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("show", "show__movie", "show__venue", "show__venue__city")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == Booking.StatusChoices.CANCELLED:
            return Response(
                {"detail": "Booking already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.cancel()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
