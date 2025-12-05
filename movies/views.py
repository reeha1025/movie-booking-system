from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.http import HttpResponse
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def movie_list(request):
    search_query = request.GET.get('search')
    language = request.GET.get('language')
    genre = request.GET.get('genre')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    fmt = request.GET.get('format')

    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(name__icontains=search_query)
    if language:
        movies = movies.filter(language=language)
    if genre:
        movies = movies.filter(genre=genre)
    if year_min:
        movies = movies.filter(release_year__gte=year_min)
    if year_max:
        movies = movies.filter(release_year__lte=year_max)
    if fmt:
        movies = movies.filter(theaters__format=fmt)

    movies = movies.distinct()

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'active_filters': {
            'search': search_query or '',
            'language': language or '',
            'genre': genre or '',
            'year_min': year_min or '',
            'year_max': year_max or '',
            'format': fmt or '',
        }
    })


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theater = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theater})


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theaters = get_object_or_404(Theater, id=theater_id)
    release_expired_bookings(request.user)
    seats = Seat.objects.filter(theater=theaters)

    if request.method == 'POST':
        selected_Seats = request.POST.getlist('seats')
        error_seats = []

        if not selected_Seats:
            return render(
                request,
                "movies/seat_selection.html",
                {'theaters': theaters, "seats": seats, 'error': "No seat selected"}
            )

        with transaction.atomic():
            for seat_id in selected_Seats:
                try:
                    seat = Seat.objects.select_for_update().get(id=seat_id, theater=theaters)
                except Seat.DoesNotExist:
                    error_seats.append(f"#{seat_id}")
                    continue

                if seat.is_booked:
                    error_seats.append(seat.seat_number)
                    continue

                try:
                    b = Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theaters.movie,
                        theater=theaters,
                        status=Booking.StatusChoices.PENDING,
                        payment_status=Booking.PaymentStatus.PENDING,
                        expires_at=timezone.now() + timedelta(minutes=5)
                    )
                    seat.is_booked = True
                    seat.save(update_fields=["is_booked"])
                except IntegrityError:
                    error_seats.append(seat.seat_number)

        if error_seats:
            error_message = f"The following seats are already booked: {', '.join(error_seats)}"
            return render(
                request,
                'movies/seat_selection.html',
                {'theaters': theaters, "seats": seats, 'error': error_message}
            )

        return redirect('checkout', theater_id=theaters.id)

    return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats})


def release_expired_bookings(user):
    expired = Booking.objects.filter(user=user, status=Booking.StatusChoices.PENDING, expires_at__lt=timezone.now())
    for b in expired.select_related('seat'):
        if b.seat:
            b.seat.is_booked = False
            b.seat.save(update_fields=["is_booked"])
        b.status = Booking.StatusChoices.CANCELLED
        b.payment_status = Booking.PaymentStatus.REFUNDED
        b.save(update_fields=["status", "payment_status"])


@login_required(login_url='/login/')
def checkout(request, theater_id):
    theaters = get_object_or_404(Theater, id=theater_id)
    release_expired_bookings(request.user)
    bookings = Booking.objects.filter(user=request.user, theater=theaters, status=Booking.StatusChoices.PENDING).select_related('seat')
    total = sum([theaters.price for _ in bookings])
    return render(request, 'movies/checkout.html', {'theaters': theaters, 'bookings': bookings, 'total': total})


@login_required(login_url='/login/')
def pay_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id, user=request.user)
    if b.status == Booking.StatusChoices.PENDING:
        if request.method == 'POST':
            upi_app = request.POST.get('upi_app', 'gpay')
            return redirect('upi_otp', booking_id=b.id, upi_app=upi_app)
        return render(request, 'movies/upi_selection.html', {
            'booking': b,
            'amount': b.theater.price,
        })
    return redirect('profile')


@login_required(login_url='/login/')
def upi_otp(request, booking_id, upi_app):
    b = get_object_or_404(Booking, id=booking_id, user=request.user)
    if b.status != Booking.StatusChoices.PENDING:
        return redirect('profile')

    user_email = request.user.email or f"{request.user.username}@example.com"
    masked_email = user_email[:3] + '***' + user_email[user_email.find('@'):]

    if request.method == 'POST':
        return redirect('upi_scanner', booking_id=b.id)

    return render(request, 'movies/otp_verification.html', {
        'booking': b,
        'upi_app': upi_app,
        'user_email': masked_email,
    })


@login_required(login_url='/login/')
def upi_scanner(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id, user=request.user)
    if b.status != Booking.StatusChoices.PENDING:
        return redirect('profile')

    if request.method == 'POST':
        return redirect('payment_success', booking_id=b.id)

    return render(request, 'movies/qr_scanner.html', {
        'booking': b,
        'amount': b.theater.price,
    })


@login_required(login_url='/login/')
def payment_success(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id, user=request.user)

    if b.status == Booking.StatusChoices.PENDING:
        b.status = Booking.StatusChoices.CONFIRMED
        b.payment_status = Booking.PaymentStatus.PAID
        b.expires_at = None
        b.save(update_fields=["status", "payment_status", "expires_at"])

        if request.user.email:
            send_mail(
                subject='Booking Confirmation - BookMySeat',
                message=f"""
Dear {request.user.username},

Your booking is confirmed!

Movie: {b.movie.name}
Theater: {b.theater.name}
Date & Time: {b.theater.time}
Seat: {b.seat.seat_number}
Amount Paid: ₹{b.theater.price}

Thank you for booking with BookMySeat!
Enjoy your movie!
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=True
            )

    return render(request, 'movies/payment_success_final.html', {'booking': b})


@login_required(login_url='/login/')
def cancel_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id, user=request.user)
    if b.status == Booking.StatusChoices.PENDING:
        if b.seat:
            b.seat.is_booked = False
            b.seat.save(update_fields=["is_booked"])
        b.status = Booking.StatusChoices.CANCELLED
        b.payment_status = Booking.PaymentStatus.REFUNDED
        b.save(update_fields=["status", "payment_status"])
    return redirect('profile')


@staff_member_required
def analytics_dashboard(request):
    total_paid = Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED,
                                        payment_status=Booking.PaymentStatus.PAID)
    revenue = sum([b.theater.price for b in total_paid])

    popular_movies = (
        Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED)
        .values('movie__name')
        .order_by()
    )
    movie_counts = {}
    for item in popular_movies:
        name = item['movie__name']
        movie_counts[name] = movie_counts.get(name, 0) + 1

    busiest_theaters = (
        Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED)
        .values('theater__name')
        .order_by()
    )
    theater_counts = {}
    for item in busiest_theaters:
        name = item['theater__name']
        theater_counts[name] = theater_counts.get(name, 0) + 1

    movie_top = sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    theater_top = sorted(theater_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return render(request, 'admin/analytics.html', {
        'revenue': revenue,
        'movie_top': movie_top,
        'theater_top': theater_top,
    })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie).order_by('time')

    embed = None
    if movie.trailer_url:
        try:
            from urllib.parse import urlparse, parse_qs
            u = urlparse(movie.trailer_url)

            if 'youtube.com/embed/' in movie.trailer_url:
                embed = movie.trailer_url
            elif 'youtube.com' in u.netloc:
                v = parse_qs(u.query).get('v', [''])[0]
                if v:
                    embed = f'https://www.youtube.com/embed/{v}'
            elif 'youtu.be' in u.netloc:
                vid = u.path.strip('/')
                if vid:
                    embed = f'https://www.youtube.com/embed/{vid}'
        except Exception:
            embed = None

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'theaters': theaters,
        'trailer_embed_url': embed
    })


# -----------------------------------------------------------------
#   ⭐⭐⭐ ADD THIS PART — load movies.json into Vercel DB ⭐⭐⭐
# -----------------------------------------------------------------

def load_movies(request):
    try:
        call_command("loaddata", "movies.json")
        return HttpResponse("Movies loaded successfully!")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")





