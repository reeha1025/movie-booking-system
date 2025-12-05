from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegisterForm, UserUpdateForm
from movies.models import Movie, Booking, Theater, Seat
from django.utils import timezone
from datetime import timedelta


# ------------------------------------
# HOME PAGE
# ------------------------------------
def home(request):
    try:
        movies = Movie.objects.all()
        latest_movies = Movie.objects.filter(release_year__gte=2024).order_by('-release_year', '-rating')[:8]
        telugu_movies = Movie.objects.filter(language='Telugu', release_year__gte=2024).order_by('-rating')[:8]
        hindi_movies = Movie.objects.filter(language='Hindi', release_year__gte=2024).order_by('-rating')[:8]
        english_movies = Movie.objects.filter(language='English', release_year__gte=2024).order_by('-rating')[:8]
        animation_movies = Movie.objects.filter(genre='Animation', release_year__gte=2024).order_by('-rating')[:8]
        kids_movies = Movie.objects.filter(genre__in=['Animation', 'Family'], release_year__gte=2024).order_by('-rating')[:8]
    except Exception as e:
        return render(request, "error.html", {"error": str(e)})

    return render(request, 'home.html', {
        'movies': movies,
        'latest_movies': latest_movies,
        'telugu_movies': telugu_movies,
        'hindi_movies': hindi_movies,
        'english_movies': english_movies,
        'animation_movies': animation_movies,
        'kids_movies': kids_movies,
    })


# ------------------------------------
# REGISTER USER
# ------------------------------------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('profile')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


# ------------------------------------
# LOGIN
# ------------------------------------
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


# ------------------------------------
# PROFILE WITH BOOKINGS
# ------------------------------------
@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, "Profile updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'bookings': bookings,
    })


# ------------------------------------
# RESET PASSWORD
# ------------------------------------
@login_required
def reset_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # IMPORTANT fix for logout bug
            messages.success(request, "Password changed successfully!")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/reset_password.html', {'form': form})


# ------------------------------------
# HELPER FUNCTION TO RELEASE EXPIRED BOOKINGS
# ------------------------------------
def release_expired_bookings(user):
    expired = Booking.objects.filter(
        user=user, status=Booking.StatusChoices.PENDING, expires_at__lt=timezone.now()
    )
    for b in expired.select_related('seat'):
        if b.seat:
            b.seat.is_booked = False
            b.seat.save(update_fields=["is_booked"])
        b.status = Booking.StatusChoices.CANCELLED
        b.payment_status = Booking.PaymentStatus.REFUNDED
        b.save(update_fields=["status", "payment_status"])


# ------------------------------------
# DUMMY PAYMENT FLOW
# ------------------------------------
@login_required
def dummy_pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != Booking.StatusChoices.PENDING:
        return redirect('profile')
    if request.method == 'POST':
        upi_app = request.POST.get('upi_app')
        return redirect('dummy_warning', booking_id=booking.id, upi_app=upi_app)
    return render(request, 'movies/pay_booking.html', {'booking': booking})


@login_required
def dummy_warning(request, booking_id, upi_app):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        return redirect('dummy_otp', booking_id=booking.id, upi_app=upi_app)
    return render(request, 'movies/dummy_warning.html', {'booking': booking, 'upi_app': upi_app})


@login_required
def dummy_otp(request, booking_id, upi_app):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        return redirect('dummy_scanner', booking_id=booking.id)
    return render(request, 'movies/dummy_otp.html', {'booking': booking, 'upi_app': upi_app})


@login_required
def dummy_scanner(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.status = Booking.StatusChoices.CONFIRMED
        booking.payment_status = Booking.PaymentStatus.PAID
        booking.save(update_fields=['status', 'payment_status'])
        return redirect('payment_success', booking_id=booking.id)
    return render(request, 'movies/dummy_scanner.html', {'booking': booking})

