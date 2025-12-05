from django.db import models
from django.contrib.auth.models import User 

GENRE_CHOICES = [
    ('Action', 'Action'), ('Adventure', 'Adventure'), ('Animation', 'Animation'), ('Comedy', 'Comedy'),
    ('Crime', 'Crime'), ('Documentary', 'Documentary'), ('Drama', 'Drama'), ('Family', 'Family'),
    ('Fantasy', 'Fantasy'), ('Horror', 'Horror'), ('Musical', 'Musical'), ('Mystery', 'Mystery'),
    ('Romance', 'Romance'), ('Sci-Fi', 'Sci-Fi'), ('Sports', 'Sports'), ('Thriller', 'Thriller'),
    ('War', 'War'), ('Western', 'Western'), ('Biography', 'Biography'), ('History', 'History'),
]

LANGUAGE_CHOICES = [
    ('English', 'English'), ('Hindi', 'Hindi'), ('Tamil', 'Tamil'), ('Telugu', 'Telugu'),
    ('Malayalam', 'Malayalam'), ('Kannada', 'Kannada'), ('Gujarati', 'Gujarati'), ('Marathi', 'Marathi'),
    ('Punjabi', 'Punjabi'), ('Bengali', 'Bengali'), ('Urdu', 'Urdu'), ('Japanese', 'Japanese'),
    ('Korean', 'Korean'), ('French', 'French'), ('German', 'German'), ('Spanish', 'Spanish'),
    ('Chinese', 'Chinese'), ('Russian', 'Russian'), ('Arabic', 'Arabic'),
]

class Movie(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=32, choices=GENRE_CHOICES, default='Drama')
    language = models.CharField(max_length=32, choices=LANGUAGE_CHOICES, default='English')
    release_year = models.PositiveIntegerField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.genre}, {self.language})"


class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.DateTimeField()

    class FormatChoices(models.TextChoices):
        TWO_D = '2D', '2D'
        THREE_D = '3D', '3D'
        IMAX_3D = 'IMAX 3D', 'IMAX 3D'

    format = models.CharField(max_length=10, choices=FormatChoices.choices, default=FormatChoices.TWO_D)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=100)

    # New fields for amenities
    parking_available = models.BooleanField(default=True)
    wheelchair_accessible = models.BooleanField(default=True)
    emoji = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'


class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    expires_at = models.DateTimeField(blank=True, null=True)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'
