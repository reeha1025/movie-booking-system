from django.contrib import admin
from .models import Movie, Theater, Seat, Booking

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'genre', 'language', 'release_year']
    list_filter = ['language', 'genre', 'release_year']
    search_fields = ['name', 'cast']
    actions = ['set_year_2024', 'set_year_2025', 'auto_year_by_rating']

    def set_year_2024(self, request, queryset):
        updated = queryset.update(release_year=2024)
        self.message_user(request, f"Updated {updated} movies to 2024")

    def set_year_2025(self, request, queryset):
        updated = queryset.update(release_year=2025)
        self.message_user(request, f"Updated {updated} movies to 2025")

    def auto_year_by_rating(self, request, queryset):
        updated = 0
        for m in queryset:
            try:
                r = float(m.rating)
            except Exception:
                r = 0.0
            m.release_year = 2025 if r >= 8.0 else 2024
            m.save(update_fields=['release_year'])
            updated += 1
        self.message_user(request, f"Auto-assigned release_year for {updated} movies")
    set_year_2024.short_description = "Set release year to 2024"
    set_year_2025.short_description = "Set release year to 2025"
    auto_year_by_rating.short_description = "Auto assign year by rating"

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie', 'time', 'format', 'price']
    list_filter = ['format', 'movie']
    actions = ['mark_2d', 'mark_3d', 'mark_imax3d', 'set_price_200', 'set_price_300']

    def mark_2d(self, request, queryset):
        updated = queryset.update(format=Theater.FormatChoices.TWO_D)
        self.message_user(request, f"Updated {updated} theaters to 2D")

    def mark_3d(self, request, queryset):
        updated = queryset.update(format=Theater.FormatChoices.THREE_D)
        self.message_user(request, f"Updated {updated} theaters to 3D")

    def mark_imax3d(self, request, queryset):
        updated = queryset.update(format=Theater.FormatChoices.IMAX_3D)
        self.message_user(request, f"Updated {updated} theaters to IMAX 3D")
    mark_2d.short_description = "Set format to 2D"
    mark_3d.short_description = "Set format to 3D"
    mark_imax3d.short_description = "Set format to IMAX 3D"

    def set_price_200(self, request, queryset):
        updated = queryset.update(price=200)
        self.message_user(request, f"Set price ₹200 for {updated} theaters")

    def set_price_300(self, request, queryset):
        updated = queryset.update(price=300)
        self.message_user(request, f"Set price ₹300 for {updated} theaters")
    set_price_200.short_description = "Set price to ₹200"
    set_price_300.short_description = "Set price to ₹300"

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'booked_at']
