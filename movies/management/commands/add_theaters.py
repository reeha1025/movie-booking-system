from django.core.management.base import BaseCommand
from movies.models import Movie, Theater
from django.utils import timezone
from random import randint, choice
from datetime import timedelta

class Command(BaseCommand):
    help = 'Add 3 theaters for each movie with random times and prices'

    def handle(self, *args, **options):
        format_choices = [Theater.FormatChoices.TWO_D, Theater.FormatChoices.THREE_D, Theater.FormatChoices.IMAX_3D]

        for movie in Movie.objects.all():
            for i in range(1, 4):  # 3 theaters per movie
                name = f"{movie.name} Theater {i}"
                time = timezone.now() + timedelta(days=randint(0,5), hours=randint(10,22))
                price = randint(100, 150)
                format_choice = choice(format_choices)

                theater, created = Theater.objects.get_or_create(
                    name=name,
                    movie=movie,
                    time=time,
                    format=format_choice,
                    price=price
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created {name}"))
                else:
                    self.stdout.write(f"{name} already exists")
