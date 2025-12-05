from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.management import call_command
import random
import stripe
from django.conf import settings
from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY


# ----------------- MOVIE LIST -----------------
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


# ----------------- MOVIE DETAIL -----------------
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


# ----------------- THEATER LIST -----------------
def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})


# ----------------- RELEASE EXPIRED BOOKINGS -----------------
def release_expired_bookings():
    expired = Booking.objects.filter(
        status=Booking.StatusChoices.PENDING,
        expires_at__lt=timezone.now()
    )
    for b in expired.select_related('seat'):
        if b.seat:
            b.seat.is_booked = False
            b.seat.save(update_fields=["is_booked"])
        b.status = Booking.StatusChoices.CANCELLED
        b.payment_status = Booking.PaymentStatus.REFUNDED
        b.expires_at = None
        b.save(update_fields=["status", "payment_status", "expires_at"])


# ----------------- BOOK SEATS -----------------
@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    release_expired_bookings()
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        error_seats = []

        if not selected_seats:
            return render(request, "movies/seat_selection.html",
                          {'theater': theater, "seats": seats, 'error': "No seat selected"})

        with transaction.atomic():
            for seat_id in selected_seats:
                try:
                    seat = Seat.objects.select_for_update().get(id=seat_id, theater=theater)
                except Seat.DoesNotExist:
                    error_seats.append(f"#{seat_id}")
                    continue

                if seat.is_booked:
                    error_seats.append(seat.seat_number)
                    continue

                try:
                    Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theater.movie,
                        theater=theater,
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
            return render(request, 'movies/seat_selection.html',
                          {'theater': theater, "seats": seats, 'error': error_message})

        return redirect('checkout', theater_id=theater.id)

    return render(request, 'movies/seat_selection.html', {'theater': theater, "seats": seats})


# ----------------- CHECKOUT -----------------
@login_required(login_url='/login/')
def checkout(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    release_expired_bookings()
    bookings = Booking.objects.filter(
        user=request.user, theater=theater, status=Booking.StatusChoices.PENDING
    ).select_related('seat')
    total = sum([theater.price for _ in bookings])
    return render(request, 'movies/checkout.html', {'theater': theater, 'bookings': bookings, 'total': total})


# ----------------- PAYMENT FLOW (DUMMY) -----------------
@login_required(login_url='/login/')
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == Booking.StatusChoices.PENDING:
        if request.method == 'POST':
            upi_app = request.POST.get('upi_app', 'gpay')
            return redirect('upi_otp', booking_id=booking.id, upi_app=upi_app)
        return render(request, 'movies/upi_selection.html', {'booking': booking, 'amount': booking.theater.price})
    return redirect('profile')


@login_required(login_url='/login/')
def upi_otp(request, booking_id, upi_app):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != Booking.StatusChoices.PENDING:
        return redirect('profile')

    masked_email = (request.user.email[:3] + '***' + request.user.email.split('@')[1]) \
        if request.user.email else f"{request.user.username}@example.com"

    if request.method == 'POST':
        return redirect('upi_scanner', booking_id=booking.id)

    return render(request, 'movies/otp_verification.html', {
        'booking': booking,
        'upi_app': upi_app,
        'user_email': masked_email,
    })


@login_required(login_url='/login/')
def upi_scanner(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != Booking.StatusChoices.PENDING:
        return redirect('profile')

    if request.method == 'POST':
        return redirect('payment_success', booking_id=booking.id)

    return render(request, 'movies/qr_scanner.html', {'booking': booking, 'amount': booking.theater.price})


@login_required(login_url='/login/')
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == Booking.StatusChoices.PENDING:
        booking.status = Booking.StatusChoices.CONFIRMED
        booking.payment_status = Booking.PaymentStatus.PAID
        booking.expires_at = None
        booking.save(update_fields=["status", "payment_status", "expires_at"])

        if request.user.email:
            send_booking_email(request.user, booking)

    return render(request, 'movies/payment_success_final.html', {'booking': booking})


@login_required(login_url='/login/')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == Booking.StatusChoices.PENDING:
        if booking.seat:
            booking.seat.is_booked = False
            booking.seat.save(update_fields=["is_booked"])
        booking.status = Booking.StatusChoices.CANCELLED
        booking.payment_status = Booking.PaymentStatus.REFUNDED
        booking.expires_at = None
        booking.save(update_fields=["status", "payment_status", "expires_at"])
    return redirect('profile')


# ----------------- ANALYTICS DASHBOARD -----------------
@staff_member_required
def analytics_dashboard(request):
    total_paid = Booking.objects.filter(
        status=Booking.StatusChoices.CONFIRMED,
        payment_status=Booking.PaymentStatus.PAID
    )
    revenue = sum([b.theater.price for b in total_paid])

    popular_movies = Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED).values('movie__name')
    movie_counts = {}
    for item in popular_movies:
        name = item['movie__name']
        movie_counts[name] = movie_counts.get(name, 0) + 1

    busiest_theaters = Booking.objects.filter(status=Booking.StatusChoices.CONFIRMED).values('theater__name')
    theater_counts = {}
    for item in busiest_theaters:
        name = item['theater__name']
        theater_counts[name] = theater_counts.get(name, 0) + 1

    movie_top = sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    theater_top = sorted(theater_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return render(request, 'admin/analytics.html', {'revenue': revenue, 'movie_top': movie_top, 'theater_top': theater_top})


# ----------------- LOAD MOVIES JSON -----------------
@staff_member_required
def load_movies(request):
    try:
        call_command("loaddata", "movies.json")
        return HttpResponse("Movies loaded successfully!")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


# ----------------- ADD THEATERS AUTOMATICALLY -----------------
@staff_member_required
def add_theaters_view(request):
    movies = Movie.objects.all()
    formats = ['2D', '3D', 'IMAX 3D']
    emoji_info = {
        'Action': '🎯🚗♿',
        'Comedy': '😂🍿♿',
        'Drama': '🎭☕♿',
        'Fantasy': '🧚‍♂️🏰♿',
        'Animation': '🐭🎨♿',
        'Horror': '👻🩸♿',
        'Romance': '💖🌹♿',
        'Sci-Fi': '🛸🤖♿',
    }

    for movie in movies:
        for i in range(1, 4):
            theater_name = f"{movie.name} Theater {i}"
            emojis = emoji_info.get(movie.genre, '🎬♿')
            theater_name_with_emoji = f"{theater_name} {emojis}"

            time = datetime.now() + timedelta(days=i, hours=random.randint(10, 22))
            format_choice = random.choice(formats)
            price = random.randint(100, 150)

            if not movie.theaters.filter(name=theater_name_with_emoji, time=time).exists():
                theater = movie.theaters.create(
                    name=theater_name_with_emoji,
                    time=time,
                    format=format_choice,
                    price=price
                )
                for s in range(1, 31):
                    theater.seats.create(seat_number=f"S{s:02}")

    return HttpResponse("3 theaters added for each movie successfully!")


# ----------------- RUN MIGRATIONS TEMPORARY -----------------
@staff_member_required
def run_migrations(request):
    try:
        call_command("migrate")
        return HttpResponse("Migrations ran successfully!")
    except Exception as e:
        return HttpResponse(f"Error running migrations: {str(e)}")


# ----------------- TEMP ADMIN -----------------
@staff_member_required
def create_temp_admin(request):
    if User.objects.filter(username="tempadmin").exists():
        return HttpResponse("Temp admin already exists.")

    User.objects.create_superuser(
        username="tempadmin",
        email="temp@admin.com",
        password="TempAdmin123"
    )
    return HttpResponse("Temporary admin created. Use username: tempadmin, password: TempAdmin123")


# ----------------- SEND BOOKING EMAIL -----------------
def send_booking_email(user, booking):
    subject = "🎬 Ticket Confirmation - BookMySeat"
    message = f"""
Hello {user.username},

Your movie ticket is confirmed! 🎉

Movie: {booking.movie.name}
Theater: {booking.theater.name}
Show Time: {booking.theater.time.strftime('%d %b %Y, %I:%M %p')}
Seat No: {booking.seat.seat_number}
Amount Paid: ₹{booking.theater.price}

Enjoy your movie! 🍿
Thank you for booking with BookMySeat.
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True
    )
