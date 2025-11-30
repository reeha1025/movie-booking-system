# BookMySeat - Movie Ticket Booking System 🎬

A full-featured Django-based movie ticket booking application with user authentication, seat selection, UPI payment processing, and email confirmations.

## 🚀 Live Demo

**Visit Now**: https://1068fbf9-4d7f-4817-9cc8-18e5a2a2a74b-00-9a8kaybjn0dz.pike.replit.dev/

Browse movies, select seats, and complete demo bookings!

## ✨ Key Features

- **Movie Filters**: Filter by genre (15+ options), language (19+ options), year, and format
- **Seat Selection**: Choose seats with 5-minute automatic reservation timeout
- **User Authentication**: Secure login and registration system
- **Email Confirmations**: Automatic booking confirmation emails
- **Movie Trailers**: YouTube trailer embeds on movie pages
- **UPI Payment Flow**: Demo payment with Google Pay & PhonePe options
- **Admin Dashboard**: Analytics dashboard (hidden for security)

## 🛠 Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Django Templates + Bootstrap 5
- **Payment**: Custom UPI Flow (Dummy)
- **Media**: Pillow for image processing

## 📦 Project Structure

```
movie-booking-system/
│
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── manage.py                          # Django management script
│
├── bookmyseat/                        # Main Django project settings
│   ├── settings.py                    # Django configuration
│   ├── urls.py                        # Root URL routing
│   └── wsgi.py                        # WSGI entry point
│
├── movies/                            # Movie & Booking app
│   ├── migrations/                    # Database migrations
│   ├── templates/movies/              # Movie-related templates
│   │   ├── movie_list.html
│   │   ├── movie_detail.html
│   │   ├── seat_selection.html
│   │   ├── upi_selection.html
│   │   ├── otp_verification.html
│   │   ├── qr_scanner.html
│   │   └── payment_success_final.html
│   ├── models.py                      # Database models
│   ├── views.py                       # View logic
│   └── urls.py                        # App URL routing
│
├── users/                             # User authentication app
│   ├── migrations/
│   ├── templates/users/               # Auth templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── basic.html                 # Base template
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
│
├── templates/                         # Global templates
│   └── base.html                      # Base template
│
├── static/                            # Global static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                             # Movie posters
│   └── movies/
│
└── db.sqlite3                         # SQLite database
```

## 🎨 Design Features

- Dark-themed premium UI
- Black navbar with BookMyShow logo
- Green payment elements (#10B981)
- Fully mobile responsive
- Confetti animation on successful payment
- Dummy OTP popup warning

## 🔒 Security

- CSRF protection enabled
- Secure session management
- Password hashing with Django built-in functions
- SQL injection protection via Django ORM
- XSS protection in templates
- Hidden admin panel for security

## ⚠️ Important Notes

- This is a **demonstration/dummy booking system**
- No real payments are processed
- OTP verification is simulated - enter any 4-digit code
- All features are for demo purposes only
