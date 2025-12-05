from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('<int:movie_id>/theaters', views.theater_list, name='theater_list'),
    path('theater/<int:theater_id>/seats/book/', views.book_seats, name='book_seats'),
    path('theater/<int:theater_id>/checkout/', views.checkout, name='checkout'),
    path('bookings/<int:booking_id>/pay/', views.pay_booking, name='pay_booking'),
    path('bookings/<int:booking_id>/otp/<str:upi_app>/', views.upi_otp, name='upi_otp'),
    path('bookings/<int:booking_id>/scanner/', views.upi_scanner, name='upi_scanner'),
    path('bookings/<int:booking_id>/payment-success/', views.payment_success, name='payment_success'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('add-theaters/', views.add_theaters_view, name='add_theaters'),  # ✅ Added temporary view
    path("create-temp-admin/", views.create_temp_admin, name="create_temp_admin"),
    from movies.views import run_migrations

urlpatterns += [
    path("run-migrations/", run_migrations, name="run_migrations"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]



]


