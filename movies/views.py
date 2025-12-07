from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from .models import Movie, Theater, Seat, Booking, GENRE_CHOICES, LANGUAGE_CHOICES
import io
from django.conf import settings
from datetime import datetime, timedelta
import random
import razorpay 

def cleanup_expired_bookings():
    """Cancels pending bookings that have expired and frees the seats."""
    expired_time = timezone.now()
    expired_bookings = Booking.objects.filter(
        status=Booking.StatusChoices.PENDING,
        expires_at__lt=expired_time
    )
    for booking in expired_bookings:
        # Free the seat
        seat = booking.seat
        seat.is_booked = False
        seat.save()
        
        # Mark booking as cancelled
        booking.status = Booking.StatusChoices.CANCELLED
        booking.save()

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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
            'release_year': 2012,
            'trailer_url': 'https://www.youtube.com/watch?v=eOrNdBpGMv8'
        },
        {
            'name': 'Inception',
            'image': 'movies/IQsBhg9t747dLhjXfsChIGZy4XfugER8BF0Gw5MDhIcnY5nTA1.jpg',
            'rating': 8.8,
            'cast': 'Leonardo DiCaprio, Tom Hardy, Ellen Page, Marion Cotillard',
            'description': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'genre': 'Sci-Fi',
            'language': 'English',
            'release_year': 2010,
            'trailer_url': 'https://www.youtube.com/watch?v=YoHD9XEInc0'
        },
        {
            'name': 'The Dark Knight',
            'image': 'movies/download.jpeg',
            'rating': 9.0,
            'cast': 'Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine',
            'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.',
            'genre': 'Action',
            'language': 'English',
            'release_year': 2008,
            'trailer_url': 'https://www.youtube.com/watch?v=EXeTwQWrcwY'
        },
        {
            'name': 'Interstellar',
            'image': 'movies/f5VK0h2bprRhR6iRrixcuEfRxSUF4l14F66vQYrsJGmKZ5nTA1.jpg',
            'rating': 8.6,
            'cast': 'Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine',
            'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'genre': 'Sci-Fi',
            'language': 'English',
            'release_year': 2014,
            'trailer_url': 'https://www.youtube.com/watch?v=zSWdZVtXT7E'
        },
        {
            'name': 'The Matrix',
            'image': 'movies/feUv2SYumXlT8E2RhzlYbZxfEGLG5AVrCPxP1gmAaCusxyPnA1.jpg',
            'rating': 8.7,
            'cast': 'Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving',
            'description': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
            'genre': 'Sci-Fi',
            'language': 'English',
            'release_year': 1999,
            'trailer_url': 'https://www.youtube.com/watch?v=vKQi3bBA1y8'
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
    genre = request.GET.get('genre')
    language = request.GET.get('language')
    
    if genre:
        movies = movies.filter(genre=genre)
    if language:
        movies = movies.filter(language=language)
        
    context = {
        'movies': movies,
        'genre_choices': GENRE_CHOICES,
        'language_choices': LANGUAGE_CHOICES,
        'selected_genre': genre,
        'selected_language': language
    }
    return render(request, 'movies/movie_list.html', context)

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'theaters': theaters,
        'trailer_embed_url': movie.youtube_embed_url
    })

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})

@login_required
def book_seats(request, theater_id):
    # Cleanup expired bookings before showing availability
    cleanup_expired_bookings()
    
    theater = get_object_or_404(Theater, pk=theater_id)
    seats = Seat.objects.filter(theater=theater)
    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        
        # Double check availability
        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, pk=seat_id)
            if seat.is_booked:
                # Handle error - seat taken
                return redirect('book_seats', theater_id=theater.id)

        # Redirect to checkout with selected seats as query params
        query_string = "&".join([f"seats={s}" for s in selected_seats])
        return redirect(f"/movies/theater/{theater.id}/checkout/?{query_string}") 
    return render(request, 'movies/seat_selection.html', {'theater': theater, 'seats': seats})

@login_required
def checkout(request, theater_id):
    theater = get_object_or_404(Theater, pk=theater_id)
    seats_selected = request.GET.getlist('seats')
    
    # Create a pending booking for the first seat found (simplified for this task constraints)
    # Ideally should handle multiple seats, but model links Booking to one Seat.
    # We will assume single seat booking or just pick one for the demo flow.
    # Or creating multiple bookings? The simplified task implies "Booking" object.
    # Let's create one Booking for the first seat.
    
    if not seats_selected:
        return redirect('theater_list', movie_id=theater.movie.id)

    seat_id = seats_selected[0]
    seat = get_object_or_404(Seat, pk=seat_id)
    
    # Check if seat is already booked by another user
    if seat.is_booked:
        existing_booking = Booking.objects.filter(seat=seat, status__in=[Booking.StatusChoices.CONFIRMED, Booking.StatusChoices.PENDING]).exclude(user=request.user).first()
        if existing_booking:
             return redirect('book_seats', theater_id=theater.id)

    # Create or update pending booking
    expires_at = timezone.now() + timedelta(minutes=5)
    booking, created = Booking.objects.get_or_create(
        user=request.user,
        seat=seat,
        movie=theater.movie,
        theater=theater,
        defaults={
            'status': Booking.StatusChoices.PENDING,
            'expires_at': expires_at
        }
    )
    
    # If booking existed but was expired/cancelled (re-booking logic), update it
    if not created:
        if booking.status == Booking.StatusChoices.CANCELLED or (booking.expires_at and booking.expires_at < timezone.now()):
             booking.status = Booking.StatusChoices.PENDING
             booking.expires_at = expires_at
             booking.save()
    
    # Mark seat as booked temporarily
    seat.is_booked = True
    seat.save()
    
    # Create Razorpay Order
    amount = int(theater.price * 100) # Amount in paise
    currency = "INR"
    
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': currency,
        'payment_capture': '1'
    })
    
    booking.payment_intent_id = razorpay_order['id']
    booking.save()
    
    context = {
        'theater': theater,
        'booking': booking,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': request.build_absolute_uri(f'/bookings/callback/')
    }
    return render(request, 'movies/checkout.html', context)

@login_required
def payment_callback(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify Signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Get Booking
            booking = Booking.objects.get(payment_intent_id=razorpay_order_id)
            
            # Use existing payment_success view logic (but we can redirect or call it)
            # We'll basically reproduce the success logic or redirect to success url
            # But the success view expects booking_id.
            
            return redirect('payment_success', booking_id=booking.id)
            
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'movies/payment_failure.html')
        except Exception as e:
            print(e)
            return render(request, 'movies/payment_failure.html')
    else:
        return redirect('movie_list')

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
    
    # Send Confirmation Email
    try:
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
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email sending failed: {e}")
        # Continue rendering success page even if email fails

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
        
    # 1. Total Revenue
    revenue_data = Booking.objects.filter(payment_status=Booking.PaymentStatus.PAID).aggregate(
        total=Sum('theater__price')
    )
    total_revenue = revenue_data['total'] or 0
    
    # 2. Total Bookings
    total_bookings = Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED).count()
    
    # 3. Popular Movies (for Chart)
    popular_movies = Movie.objects.annotate(
        num_bookings=Count('booking', filter=models.Q(booking__status=Booking.StatusChoices.CONFIRMED))
    ).order_by('-num_bookings')[:5]
    
    movie_labels = [m.name for m in popular_movies]
    movie_data = [m.num_bookings for m in popular_movies]
    
    # 4. Peak Theater Timings
    # Group by hour of the show
    peak_times = Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED).values('theater__time__hour').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Simple formatting for time labels
    time_labels = [f"{t['theater__time__hour']}:00" for t in peak_times]
    time_data = [t['count'] for t in peak_times]

    context = {
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'movie_labels': movie_labels,
        'movie_data': movie_data,
        'time_labels': time_labels,
        'time_data': time_data
    }
    return render(request, 'movies/admin_dashboard.html', context)

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

