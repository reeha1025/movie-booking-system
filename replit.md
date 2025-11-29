# BookMySeat - Movie Ticket Booking System

## Overview
BookMySeat is a full-featured Django-based movie ticket booking application that allows users to browse movies, select theaters and showtimes, book seats, and process payments through Stripe integration.

## Project Architecture

### Technology Stack
- **Backend Framework**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Payment Gateway**: Stripe
- **Frontend**: Django Templates with Bootstrap
- **Media Handling**: Pillow for image processing
- **Deployment**: Gunicorn WSGI server

### Core Applications
1. **movies**: Handles movie listings, theaters, seat bookings, and payments
2. **users**: Manages user authentication, registration, and profiles

### Implemented Features (All 6 Tasks Complete)

1. **Genre and Language Filters** ✅
   - Filter movies by genre (Action, Comedy, Drama, etc.)
   - Filter by language (Hindi, English, Telugu, Tamil, etc.)
   - Additional filters for year range and format (2D, 3D, IMAX)
   - Located in: `movies/views.py` - `movie_list()`

2. **Ticket Email Confirmation** ✅
   - Sends booking confirmation email after successful payment
   - Includes movie name, theater, showtime, seat number, and amount
   - Located in: `movies/views.py` - `payment_success()`

3. **Movie Trailers** ✅
   - Embeds YouTube trailers on movie detail pages
   - Supports both youtube.com and youtu.be URLs
   - Located in: `movies/views.py` - `movie_detail()`

4. **Payment Gateway (Stripe)** ✅
   - Full Stripe PaymentIntent integration
   - Test mode for development (no real charges)
   - Success/failure handling with appropriate UI
   - Located in: `movies/views.py` - `pay_booking()`, `payment_success()`

5. **Seat Reservation Timeout** ✅
   - Seats reserved for 5 minutes during checkout
   - Automatic release of expired reservations
   - Located in: `movies/views.py` - `release_expired_bookings()`

6. **Admin Dashboard with Analytics** ✅
   - Total revenue from confirmed bookings
   - Top 10 most popular movies by booking count
   - Top 10 busiest theaters by booking count
   - Access at: `/admin/analytics/` (requires admin login)
   - Located in: `movies/views.py` - `analytics_dashboard()`

### Other Features
- User authentication and profile management
- Responsive dark-themed UI
- Media file handling for movie posters

## Recent Changes (November 29, 2025)

### Initial Replit Environment Setup
- Installed Python 3.12 and all required dependencies
- Configured Django settings to allow all hosts for Replit proxy
- Set up SQLite database for development (migrations applied)
- Collected static files for Django admin and application
- Configured workflow to run Django dev server on 0.0.0.0:5000
- Set up deployment configuration using Gunicorn on autoscale
- Application successfully running and accessible

### Configuration Updates
- Modified `ALLOWED_HOSTS` to include Replit domains (`.replit.dev`, `.replit.app`, `.repl.co`)
- Added Replit domains to `CSRF_TRUSTED_ORIGINS`
- Set `USE_SQLITE` environment variable to force SQLite usage in development
- Database configuration now gracefully handles PostgreSQL when available
- Created admin superuser for analytics dashboard access

## Environment Setup

### Development Environment Variables
- `USE_SQLITE=1`: Forces SQLite usage (set by default in Replit)
- `DEBUG=True`: Enables debug mode (default)
- `SECRET_KEY`: Django secret key (uses fallback in development)

### Production Environment Variables (Required)
- `SECRET_KEY`: Secure random string for Django
- `DEBUG=False`: Disable debug mode
- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_SECRET_KEY`: Stripe API secret key
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key
- `EMAIL_HOST_USER`: SMTP email address
- `EMAIL_HOST_PASSWORD`: SMTP app password

### Optional Environment Variables
- `STRIPE_TEST_MODE=True`: Use mock payment processing (default: True)

## Database

### Current Setup
- **Development**: SQLite database (`db.sqlite3`)
- **Production**: PostgreSQL (configured via `DATABASE_URL`)

### Migrations
All migrations have been applied. The database includes:
- User authentication tables
- Movie, Theater, and Seat models
- Booking system with payment tracking
- Session management

### Existing Data
The imported database contains sample movies with images in the `media/movies/` directory.

## Running the Application

### Development Server
The workflow "Start Django Server" is configured to run:
```bash
python manage.py runserver 0.0.0.0:5000
```

Access the application through the Replit webview preview.

### Production Deployment
The deployment is configured for autoscale with:
- **Build**: `python manage.py collectstatic --noinput`
- **Run**: `gunicorn --bind=0.0.0.0:5000 --reuse-port bookmyseat.wsgi:application`

## Admin Access

### Creating a Superuser
```bash
python manage.py createsuperuser
```

### Admin Panel
Access at `/admin/` to manage:
- Movies and theaters
- Bookings and payments
- Users
- Analytics dashboard at `/admin/analytics/`

## File Structure

```
bookmyseat/          # Main Django project settings
├── settings.py      # Django configuration
├── urls.py          # Root URL configuration
├── wsgi.py          # WSGI application entry point

movies/              # Movies and booking app
├── models.py        # Movie, Theater, Seat, Booking models
├── views.py         # View logic for listings, bookings, payments
├── urls.py          # URL routing

users/               # User management app
├── views.py         # Authentication, registration, profile
├── forms.py         # User forms
├── urls.py          # URL routing

templates/           # HTML templates
├── home.html        # Homepage
├── movies/          # Movie-related templates
├── users/           # User-related templates

static/              # Static assets (CSS, JS, images)
media/               # Uploaded media files (movie posters)
staticfiles/         # Collected static files for production

db.sqlite3           # SQLite database (development)
manage.py            # Django management script
```

## API Integration

### Stripe Payment Processing
The application integrates with Stripe for payment processing:
- Test mode enabled by default via `STRIPE_TEST_MODE`
- Payment intent creation and confirmation
- Webhook support for payment events
- Refund processing for cancelled bookings

## User Preferences
None documented yet - this is a fresh import.

## Development Notes

### Seat Booking System
- Seats have an expiration mechanism to prevent indefinite holds
- Uses Django transactions for atomic booking operations
- Real-time seat availability checking

### Payment Flow
1. User selects seats and proceeds to checkout
2. System creates a booking with PENDING status
3. Stripe payment intent is created
4. User completes payment
5. Booking status updates to CONFIRMED

### Security Features
- CSRF protection enabled
- Secure session management
- Password validation
- SQL injection protection via Django ORM
- XSS protection in templates

## Known Limitations
- Single theater per showing (no multi-theater support)
- No booking modification after creation
- Email backend uses console output in development

## Future Enhancement Ideas
- Mobile app integration
- QR code ticket generation
- Advanced analytics and reporting
- Multi-language support
- Social media integration
- Gift cards and promotions
