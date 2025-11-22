import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Theater

def update_theater_prices():
    """Update all theater prices to random values between 100 and 300"""
    
    theaters = Theater.objects.all()
    updated_count = 0
    
    print(f"Found {theaters.count()} theaters to update...")
    
    for theater in theaters:
        # Generate random price between 100 and 300
        new_price = random.randint(100, 300)
        
        # Update the price
        theater.price = new_price
        theater.save(update_fields=['price'])
        
        updated_count += 1
        print(f"Updated {theater.name} - {theater.movie.name} - New price: ₹{new_price}")
    
    print(f"\nPrice update completed! Updated {updated_count} theaters.")
    
    # Show some sample updated prices
    print("\nSample updated prices:")
    sample_theaters = Theater.objects.all()[:10]
    for theater in sample_theaters:
        print(f"{theater.name} - {theater.movie.name} - ₹{theater.price}")

if __name__ == "__main__":
    update_theater_prices()