from django.db import transaction
from rest_framework import serializers

from .models import Booking, City, Movie, Show, Venue


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "state", "slug"]
        read_only_fields = ["id", "slug"]


class VenueSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    city_slug = serializers.SlugRelatedField(
        queryset=City.objects.all(), slug_field="slug", source="city", write_only=True
    )

    class Meta:
        model = Venue
        fields = [
            "id",
            "name",
            "address",
            "contact_number",
            "amenities",
            "city",
            "city_slug",
        ]
        read_only_fields = ["id", "city"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "release_date",
            "language",
            "censor_rating",
        ]


class ShowSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source="movie", write_only=True
    )
    venue = VenueSerializer(read_only=True)
    venue_id = serializers.PrimaryKeyRelatedField(
        queryset=Venue.objects.all(), source="venue", write_only=True
    )

    class Meta:
        model = Show
        fields = [
            "id",
            "movie",
            "movie_id",
            "venue",
            "venue_id",
            "show_time",
            "screen",
            "available_seats",
            "language",
            "format",
            "price",
            "is_active",
        ]
        read_only_fields = ["id", "available_seats", "is_active", "movie", "venue"]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    show = ShowSerializer(read_only=True)
    show_id = serializers.PrimaryKeyRelatedField(
        queryset=Show.objects.filter(is_active=True), source="show", write_only=True
    )
    booked_at = serializers.DateTimeField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "reference_code",
            "user",
            "show",
            "show_id",
            "seats",
            "status",
            "payment_status",
            "booked_at",
            "total_amount",
        ]
        read_only_fields = [
            "id",
            "reference_code",
            "user",
            "status",
            "payment_status",
            "booked_at",
            "total_amount",
            "show",
        ]

    def validate_seats(self, value):
        if value <= 0:
            raise serializers.ValidationError("Seats must be greater than zero.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        show = validated_data["show"]
        seats = validated_data["seats"]

        with transaction.atomic():
            show_locked = Show.objects.select_for_update().get(pk=show.pk)
            if not show_locked.is_active:
                raise serializers.ValidationError(
                    {"show_id": "Selected show is no longer available."}
                )
            if show_locked.available_seats < seats:
                raise serializers.ValidationError(
                    {"seats": "Not enough seats available for this show."}
                )
            show_locked.reserve_seats(seats)
            booking = Booking.objects.create(user=user, show=show_locked, seats=seats)
        return booking
