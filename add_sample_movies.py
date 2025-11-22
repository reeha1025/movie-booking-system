import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie, Theater
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

def create_sample_movies():
    """Create sample movies based on available images"""
    
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
    
    # Create movies
    created_movies = []
    for movie_data in movies_data:
        movie, created = Movie.objects.get_or_create(
            name=movie_data['name'],
            defaults=movie_data
        )
        if created:
            created_movies.append(movie)
            print(f"Created movie: {movie.name}")
        else:
            print(f"Movie already exists: {movie.name}")
    
    return created_movies

def create_sample_theaters():
    """Create sample theaters for movies"""
    theaters_data = [
        {'name': 'PVR Cinemas', 'format': '2D'},
        {'name': 'INOX', 'format': '3D'},
        {'name': 'Cinepolis', 'format': 'IMAX 3D'},
        {'name': 'Miraj Cinemas', 'format': '2D'},
    ]
    
    movies = Movie.objects.all()
    created_theaters = []
    
    for movie in movies:
        for theater_data in theaters_data:
            # Create showtimes for today and next 3 days
            for day_offset in range(4):
                base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=day_offset)
                
                # Create 3 showtimes per day
                for hour_offset in [0, 6, 12]:  # 10 AM, 4 PM, 10 PM
                    showtime = base_time + timedelta(hours=hour_offset)
                    
                    # Generate random price between 100 and 300
                    random_price = random.randint(100, 300)
                    
                    theater, created = Theater.objects.get_or_create(
                        name=theater_data['name'],
                        movie=movie,
                        time=showtime,
                        defaults={
                            'format': theater_data['format'],
                            'price': random_price
                        }
                    )
                    
                    if created:
                        created_theaters.append(theater)
                        print(f"Created theater: {theater.name} for {movie.name} at {showtime} - Price: ₹{random_price}")
    
    return created_theaters

def create_sample_seats():
    """Create sample seats for theaters"""
    from movies.models import Seat
    
    theaters = Theater.objects.all()
    created_seats = []
    
    for theater in theaters:
        # Create seats A1-A10, B1-B10, C1-C10
        for row in ['A', 'B', 'C']:
            for seat_num in range(1, 11):
                seat_number = f"{row}{seat_num}"
                seat, created = Seat.objects.get_or_create(
                    theater=theater,
                    seat_number=seat_number,
                    defaults={'is_booked': False}
                )
                if created:
                    created_seats.append(seat)
    
    print(f"Created {len(created_seats)} seats")
    return created_seats

if __name__ == "__main__":
    print("Creating sample movies...")
    movies = create_sample_movies()
    
    print("\nCreating sample theaters...")
    theaters = create_sample_theaters()
    
    print("\nCreating sample seats...")
    seats = create_sample_seats()
    
    print(f"\nSample data creation completed!")
    print(f"Movies: {len(movies)}")
    print(f"Theaters: {len(theaters)}")
    print(f"Seats: {len(seats)}")