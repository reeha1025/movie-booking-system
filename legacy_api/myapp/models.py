from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

User = get_user_model()


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class City(models.Model):
    name = models.CharField(max_length=120)
    state = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        if self.state:
            return f"{self.name}, {self.state}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while City.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Venue(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="venues")
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    amenities = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.city}"


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    language = models.CharField(max_length=40, default="English")
    censor_rating = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Show(models.Model):
    class FormatChoices(models.TextChoices):
        TWO_D = "2D", "2D"
        THREE_D = "3D", "3D"
        IMAX = "IMAX", "IMAX"
        FOUR_DX = "4DX", "4DX"

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="shows")
    show_time = models.DateTimeField()
    screen = models.CharField(max_length=50)
    available_seats = models.PositiveIntegerField()
    language = models.CharField(max_length=40, default="English")
    format = models.CharField(max_length=10, choices=FormatChoices.choices, default=FormatChoices.TWO_D)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["show_time"]

    def __str__(self):
        return f"{self.movie.title} at {self.show_time:%d %b %I:%M %p} ({self.screen})"

    def reserve_seats(self, seats: int):
        if seats <= 0:
            raise ValueError("Seats to reserve must be positive")
        if seats > self.available_seats:
            raise ValueError("Not enough seats available")
        self.available_seats -= seats
        self.save(update_fields=["available_seats"])

    def release_seats(self, seats: int):
        if seats <= 0:
            return
        self.available_seats += seats
        self.save(update_fields=["available_seats"])


class Booking(TimestampedModel):
    class StatusChoices(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="bookings")
    seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.CONFIRMED)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PAID
    )
    reference_code = models.CharField(max_length=12, unique=True, editable=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.show} ({self.seats} seats)"

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = get_random_string(12).upper()
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return (self.show.price or 0) * self.seats

    def cancel(self, refund=True):
        if self.status == self.StatusChoices.CANCELLED:
            return
        self.show.release_seats(self.seats)
        self.status = self.StatusChoices.CANCELLED
        if refund and self.payment_status == self.PaymentStatus.PAID:
            self.payment_status = self.PaymentStatus.REFUNDED
        self.save(update_fields=["status", "payment_status"])

    @property
    def booked_at(self):
        return self.created_at
