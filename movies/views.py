from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from .models import Movie, Theater, Seat, Booking
import io
from django.conf import settings

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})

@login_required
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, pk=theater_id)
    seats = Seat.objects.filter(theater=theater)
    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        # Logic to create temporary booking would go here
        # For now, just redirect to checkout with dummy booking ID
        return redirect('checkout', theater_id=theater.id) 
    return render(request, 'movies/book_seats.html', {'theater': theater, 'seats': seats})

@login_required
def checkout(request, theater_id):
    theater = get_object_or_404(Theater, pk=theater_id)
    # This view would typically take a booking ID or handle the current session's booking
    return render(request, 'movies/checkout.html', {'theater': theater})

@login_required
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'movies/pay_booking.html', {'booking': booking})

@login_required
def upi_otp(request, booking_id, upi_app):
    # Simulate OTP payment
    return render(request, 'movies/upi_otp.html', {'booking_id': booking_id, 'app': upi_app})

@login_required
def upi_scanner(request, booking_id):
    # Simulate Scanner payment
    return render(request, 'movies/upi_scanner.html', {'booking_id': booking_id})

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.payment_status = Booking.PaymentStatus.PAID
    booking.status = Booking.StatusChoices.CONFIRMED
    booking.save()
    return render(request, 'movies/payment_success.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    booking.status = Booking.StatusChoices.CANCELLED
    booking.save()
    return redirect('movie_list')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('movie_list')
    movies = Movie.objects.all()
    theaters = Theater.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'movies/admin_dashboard.html', {
        'movies_count': movies.count(),
        'theaters_count': theaters.count(),
        'bookings_count': bookings.count()
    })

@login_required
def add_theaters_view(request):
    if not request.user.is_staff:
        return redirect('movie_list')
    if request.method == 'POST':
        # Add theater logic
        pass
    return render(request, 'movies/add_theaters.html')

def create_temp_admin(request):
    # Security risk in production, but requested for dev
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            return HttpResponse("Admin created")
        return HttpResponse("Admin already exists")
    except Exception as e:
        return HttpResponse(f"Error: {e}")

def run_migrations(request):
    # Security risk in production
    output = io.StringIO()
    call_command('migrate', stdout=output)
    return HttpResponse(output.getvalue(), content_type='text/plain')

@login_required
def analytics_dashboard(request):
    if not request.user.is_staff:
        return redirect('movie_list')
    # Simple analytics
    total_revenue = Booking.objects.filter(payment_status=Booking.PaymentStatus.PAID).aggregate(
        total=Sum('theater__price')
    )['total'] or 0
    
    return render(request, 'movies/analytics_dashboard.html', {'revenue': total_revenue})
