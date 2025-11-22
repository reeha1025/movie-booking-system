from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Booking, City, Movie, Show, Venue


class BookingFlowTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='demo', password='demo1234')
        self.city = City.objects.create(name='Metropolis', state='NY', slug='metropolis')
        self.venue = Venue.objects.create(city=self.city, name='Central Cinema', address='123 Main')
        self.movie = Movie.objects.create(
            title='Example Movie',
            description='Lorem ipsum',
            duration=120,
            release_date=timezone.now().date(),
            language='English',
            censor_rating='U/A',
        )
        self.show = Show.objects.create(
            movie=self.movie,
            venue=self.venue,
            show_time=timezone.now() + timedelta(hours=4),
            screen='Screen 1',
            available_seats=50,
            language='English',
            format=Show.FormatChoices.TWO_D,
            price=250,
        )

    def test_movies_list(self):
        response = self.client.get('/api/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.movie.title)

    def test_booking_lifecycle(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/bookings/',
            {'show_id': self.show.id, 'seats': 3},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking_id = response.data['id']
        self.show.refresh_from_db()
        self.assertEqual(self.show.available_seats, 47)

        cancel_response = self.client.post(f'/api/bookings/{booking_id}/cancel/')
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        booking = Booking.objects.get(pk=booking_id)
        self.assertEqual(booking.status, Booking.StatusChoices.CANCELLED)
        self.show.refresh_from_db()
        self.assertEqual(self.show.available_seats, 50)

    def test_booking_requires_authentication(self):
        response = self.client.post(
            '/api/bookings/',
            {'show_id': self.show.id, 'seats': 2},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
