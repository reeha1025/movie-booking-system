from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
# ... (other imports unchanged) ...

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Update booking status
    booking.payment_status = Booking.PaymentStatus.PAID
    booking.status = Booking.StatusChoices.CONFIRMED
    booking.save()
    
    # Friendly transient message (useful if base template surfaces messages)
    messages.success(request, "Payment successful — thank you! Your booking is confirmed. Enjoy the movie 🎬")

    # Try to send confirmation email (optional - won't block success page)
    try:
        if booking.user.email:
            subject = f'Booking Confirmation - {booking.movie.name}'
            message = (
                f"Dear {booking.user.username},\n\n"
                f"Your booking for '{booking.movie.name}' has been confirmed!\n\n"
                f"Details:\n"
                f"Theater: {booking.theater.name}\n"
                f"Show Time: {booking.theater.time}\n"
                f"Seat: {booking.seat.seat_number}\n"
                f"Price: Rs. {booking.theater.price}\n"
                f"Booking ID: {booking.id}\n"
                f"Payment ID: {booking.payment_intent_id or 'N/A'}\n\n"
                f"Enjoy the show!\n"
                f"Team BookMySeat"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.user.email],
                fail_silently=True,
            )
    except Exception as e:
        print(f"Email sending failed: {e}")
        pass

    return render(request, 'movies/payment_success.html', {'booking': booking})




