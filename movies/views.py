from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command

from .models import Movie, Theater, Seat, Booking


# ----------------------------------------
# HOME PAGE → MOVIE LIST
# ----------------------------------------
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, "movies/movie_list.html", {"movies": movies})


# ----------------------------------------
# MOVIE DETAIL + THEATER LIST
# ----------------------------------------
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movies/movie_detail.html", {"movie": movie})


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, "movies/theater_list.html", {
        "movie": movie,
        "theaters": theaters
    })


# ----------------------------------------
# SEAT BOOKING
# ----------------------------------------
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == "POST":
        selected_seats = request.POST.getlist("seats")

        if not selected_seats:
            return HttpResponse("Please select at least one seat.")

        # Create booking
        booking = Booking.objects.create(
            theater=theater,
            seats=",".join(selected_seats),
            amount=len(selected_seats) * 120  # example price
        )
        return redirect("checkout", theater_id=theater.id)

    return render(request, "movies/book_seats.html", {
        "theater": theater,
        "seats": seats
    })


# ----------------------------------------
# CHECKOUT PAGE
# ----------------------------------------
def checkout(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    booking = Booking.objects.filter(theater=theater).last()

    if not booking:
        return HttpResponse("No booking found!")

    return render(request, "movies/checkout.html", {
        "booking": booking,
        "theater": theater
    })


# ----------------------------------------
# PAYMENT FLOW
# ----------------------------------------
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "movies/pay_booking.html", {"booking": booking})


def upi_otp(request, booking_id, upi_app):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "movies/upi_otp.html", {
        "booking": booking,
        "upi_app": upi_app
    })


def upi_scanner(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "movies/upi_scanner.html", {"booking": booking})


def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.is_paid = True
    booking.save()
    return render(request, "movies/payment_success.html", {"booking": booking})


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return HttpResponse("Booking cancelled.")


# ----------------------------------------
# ADMIN DASHBOARD
# ----------------------------------------
def admin_dashboard(request):
    movies = Movie.objects.count()
    theaters = Theater.objects.count()
    bookings = Booking.objects.count()

    return render(request, "movies/admin_dashboard.html", {
        "movies": movies,
        "theaters": theaters,
        "bookings": bookings
    })


# ----------------------------------------
# ADD THEATERS
# ----------------------------------------
def add_theaters_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        seats = request.POST.get("seats")

        Theater.objects.create(name=name, total_seats=seats)
        return HttpResponse("Theater added successfully!")

    return render(request, "movies/add_theaters.html")


# ----------------------------------------
# CREATE TEMP ADMIN (WORKS ON RENDER/VERCEL)
# ----------------------------------------
def create_temp_admin(request):
    try:
        if User.objects.filter(username="tempadmin").exists():
            return HttpResponse("Temporary admin already exists!")

        User.objects.create(
            username="tempadmin",
            password=make_password("Temp@12345"),
            is_staff=True,
            is_superuser=True
        )
        return HttpResponse("Temporary admin created! Username: tempadmin Password: Temp@12345")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


# ----------------------------------------
# RUN MIGRATIONS (SAFE)
# ----------------------------------------
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser, login_url="/")
def run_migrations(request):
    try:
        call_command("migrate")
        return HttpResponse("Migrations ran successfully!")
    except Exception as e:
        return HttpResponse(f"Error running migrations: {str(e)}")








                      
