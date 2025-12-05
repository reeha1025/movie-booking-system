# movies/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Booking
from django.conf import settings

@receiver(post_save, sender=Booking)
def send_booking_email(sender, instance, created, **kwargs):
    if created and instance.status == 'confirmed':
        subject = f"Booking Confirmation for {instance.movie.name}"
        message = (
            f"Hi {instance.user.username},\n\n"
            f"Your booking is confirmed!\n"
            f"Movie: {instance.movie.name}\n"
            f"Theater: {instance.theater.name}\n"
            f"Seat: {instance.seat.seat_number}\n"
            f"Time: {instance.theater.time}\n\n"
            "Thank you for booking with us!"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=False
        )
