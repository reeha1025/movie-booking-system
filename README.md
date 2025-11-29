# BookMySeat - Movie Ticket Booking System 🎬

A full-featured Django-based movie ticket booking application with user authentication, seat selection, UPI payment processing, and email confirmations.

## 🚀 Live Demo

**Website**: https://1068fbf9-4d7f-4817-9cc8-18e5a2a2a74b-00-9a8kaybjn0dz.pike.replit.dev/

Visit the link above to browse movies, select seats, and book tickets!

## ✨ Features

### 1. Genre & Language Filters ✅
- Filter movies by genre (15+ genres: Action, Comedy, Drama, etc.)
- Filter by language (19+ languages: Hindi, English, Telugu, Tamil, etc.)
- Additional filters for year range and format (2D, 3D, IMAX)

### 2. Ticket Email Confirmation ✅
- Automatic email confirmation after successful payment
- Includes: Movie name, theater, showtime, seat number, and amount

### 3. Movie Trailers ✅
- YouTube trailer embeds on movie detail pages
- Support for multiple URL formats

### 4. UPI Payment Flow ✅
- 2 UPI app options: Google Pay, PhonePe
- Dummy OTP verification page
- QR code scanner simulation
- Beautiful success page with confetti animation
- Green color scheme (#10B981) throughout payment flow

### 5. Seat Reservation Timeout ✅
- 5-minute automatic seat reservation
- Expired reservations automatically released
- Prevents indefinite seat holds

### 6. Email Notifications ✅
- Booking confirmations sent to user email
- Order details included in confirmation

## 🛠 Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Django Templates + Bootstrap 5
- **Payment**: Custom UPI Flow
- **Deployment**: Gunicorn on Replit
- **Media**: Pillow for image processing

## 📦 Project Structure

```
bookmyseat/              # Main Django project
├── settings.py          # Configuration
├── urls.py              # URL routing
├── wsgi.py              # WSGI entry point

movies/                  # Movie and booking app
├── models.py            # Movie, Theater, Seat, Booking models
├── views.py             # Business logic
├── urls.py              # App routes

users/                   # User authentication app
├── views.py             # Auth, registration, profile
├── forms.py             # User forms
├── urls.py              # Auth routes

templates/               # HTML templates
├── movies/              # Movie-related pages
├── users/               # Auth pages
└── base.html            # Base template

static/                  # CSS, JS, images
media/                   # Movie posters
db.sqlite3              # SQLite database
manage.py               # Django management
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/reeha1025/movie-booking-system.git
cd movie-booking-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Run development server**
```bash
python manage.py runserver 0.0.0.0:5000
```

6. **Access application**
```
Website: http://localhost:5000
```

## 🎨 Design Features

- **Dark Theme**: Premium dark-themed UI
- **Black Navbar**: BookMyShow logo branding
- **Green Payments**: #10B981 color scheme for payment elements
- **Mobile Responsive**: Works on all devices
- **Smooth Animations**: Confetti on successful payment

## 🔒 Security

- CSRF protection enabled
- Secure session management
- Password hashing
- SQL injection protection via Django ORM
- XSS protection in templates

## 📝 Environment Variables

### Development
```
USE_SQLITE=1           # Force SQLite usage
DEBUG=True             # Enable debug mode
SECRET_KEY=your-key    # Django secret key
```

### Production
```
DEBUG=False
DATABASE_URL=postgresql://...
SECRET_KEY=your-secure-key
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## 🚀 Deployment

### On Replit
1. Click **"Publish"** button in Replit dashboard
2. Select deployment configuration
3. App will be live in 2-3 minutes

### On Other Platforms (Render, Railway, etc.)
1. Push to GitHub
2. Connect repository to deployment platform
3. Configure environment variables
4. Deploy

## 📧 Email Configuration

The application sends booking confirmations via email. Configure SMTP settings in `settings.py`:

```python
EMAIL_HOST = 'your-smtp-host'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 🔧 Customization

### Add More Movies
```bash
python manage.py shell
from movies.models import Movie
Movie.objects.create(
    name='Movie Name',
    genre='Action',
    language='English',
    release_year=2024,
    trailer_url='https://www.youtube.com/embed/VIDEO_ID'
)
```

### Modify Payment Colors
Edit `templates/movies/upi_selection.html` and `templates/movies/payment_success_final.html`
- Current color: #10B981 (Green)
- Change to any hex color

## ⚠️ Known Limitations

- Single theater per showing
- No booking modification after creation
- UPI payment flow is simulated (dummy payment)
- Email backend uses console in development

## 🔮 Future Enhancements

- [ ] Real Stripe payment integration
- [ ] Mobile app
- [ ] Advanced QR code tickets
- [ ] Multi-language UI
- [ ] Social media integration
- [ ] Gift cards and promotions

## 📄 License

MIT License - feel free to use this project for your own purposes!

## 👨‍💻 Author

Built with ❤️ for movie lovers worldwide.
