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
from datetime import datetime, timedelta
import random

def populate_db(request):
    # Only allow superusers or if DEBUG is True (or for this specific debugging session)
    # Ideally should be protected, but for the user's request we'll make it accessible
    # to fix the empty DB issue.
    
    # Create Movies
    movies_data = [
        {
            'name': 'The Avengers',
            'image': 'movies/635217f73e372771013edb4c-the-avengers-poster-marvel-movie-canvas1.jpg',
            'rating': 8.5,
            'cast': 'Robert Downey Jr., Chris Evans, Mark Ruffalo, Chris Hemsworth',
            'description': 'Earth\'s mightiest heroes must come together and learn to fight as a team to stop Loki and his alien army from enslaving humanity.',
            'genre': 'Action',
            'language': 'English',
            'release_year': 2012
        },
        {
            'name': 'Inception',
            'image': 'movies/IQsBhg9t747dLhjXfsChIGZy4XfugER8BF0Gw5MDhIcnY5nTA1.jpg',
            'rating': 8.8,
            'cast': 'Leonardo DiCaprio, Tom Hardy, Ellen Page, Marion Cotillard',
            'description': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'genre': 'Sci-Fi',
            'language': 'English',
            'release_year': 2010
        },
        {
            'name': 'The Dark Knight',
            'image': 'movies/download.jpeg',
            'rating': 9.0,
            'cast': 'Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine',
            'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.',
            'genre': 'Action',
            'language': 'English',
            'release_year': 2008
        },
        {
            'name': 'Interstellar',
            'image': 'movies/f5VK0h2bprRhR6iRrixcuEfRxSUF4l14F66vQYrsJGmKZ5nTA1.jpg',
            'rating': 8.6,
            'cast': 'Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine',
            'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'genre': 'Sci-Fi',
            'language': 'English',
            'release_year': 2014
        },
        {
            'name': 'The Matrix',
            'image': 'movies/feUv2SYumXlT8E2RhzlYbZxfEGLG5AVrCPxP1gmAaCusxyPnA1.jpg',
            'rating': 8.7,
            'cast': 'Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving',
            'description': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
            'genre': 'Sci-Fi',
            'language': 'English',
            'release_year': 1999
        }
    ]
    
    created_count = 0
    for movie_data in movies_data:
        movie, created = Movie.objects.get_or_create(
            name=movie_data['name'],
            defaults=movie_data
        )
        if created:
            created_count += 1
            
            # Create Theaters for this movie
            theaters_data = [
                {'name': 'PVR Cinemas', 'format': '2D'},
                {'name': 'INOX', 'format': '3D'},
                {'name': 'Cinepolis', 'format': 'IMAX 3D'},
                {'name': 'Miraj Cinemas', 'format': '2D'},
            ]
            
            for theater_data in theaters_data:
                for day_offset in range(4):
                    base_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=day_offset)
                    for hour_offset in [0, 6, 12]:
                        showtime = base_time + timedelta(hours=hour_offset)
                        random_price = random.randint(100, 300)
                        
                        theater, t_created = Theater.objects.get_or_create(
                            name=theater_data['name'],
                            movie=movie,
                            time=showtime,
                            defaults={
                                'format': theater_data['format'],
                                'price': random_price
                            }
                        )
                        
                        # Create Seats if theater created
                        if t_created:
                            for row in ['A', 'B', 'C']:
                                for seat_num in range(1, 11):
                                    seat_number = f"{row}{seat_num}"
                                    Seat.objects.create(
                                        theater=theater,
                                        seat_number=seat_number,
                                        is_booked=False
                                    )

    return HttpResponse(f"Database populated with {created_count} new movies and associated data.")

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
    return render(request, 'movies/seat_selection.html', {'theater': theater, 'seats': seats})

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
