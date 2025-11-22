from django.contrib import admin

from .models import Booking, City, Movie, Show, Venue


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "state")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "contact_number")
    list_filter = ("city",)
    search_fields = ("name", "city__name")


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "release_date")
    search_fields = ("title",)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ("movie", "venue", "show_time", "screen", "available_seats", "is_active")
    list_filter = ("venue__city", "movie", "format", "language", "is_active")
    search_fields = ("movie__title", "venue__name")
    autocomplete_fields = ("movie", "venue")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "user", "show", "seats", "status", "payment_status", "created_at")
    list_filter = ("status", "payment_status")
    search_fields = ("reference_code", "user__username")