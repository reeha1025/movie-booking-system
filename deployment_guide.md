# Deployment Guide for BookMySeat

## Environment Variables Setup

Create a `.env` file in your project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-very-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration (PostgreSQL recommended for production)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static Files (adjust paths as needed)
STATIC_ROOT=/path/to/your/static/files
MEDIA_ROOT=/path/to/your/media/files
```

## Deployment Options

### 1. Vercel Deployment (Recommended for quick deployment)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy to Vercel:
   ```bash
   vercel
   ```

3. Set environment variables in Vercel dashboard:
   - Go to your project settings
   - Add all environment variables from your `.env` file

### 2. Heroku Deployment

1. Install Heroku CLI and login:
   ```bash
   npm install -g heroku
   heroku login
   ```

2. Create Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Add PostgreSQL database:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   # Add other variables as needed
   ```

5. Deploy:
   ```bash
   git push heroku main
   ```

### 3. Traditional VPS/Docker Deployment

1. Set up your server with Python, PostgreSQL, and Nginx
2. Clone your repository
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate --settings=bookmyseat.settings_production`
5. Collect static files: `python manage.py collectstatic --settings=bookmyseat.settings_production`
6. Configure Nginx as reverse proxy
7. Use Gunicorn as WSGI server

## Production Settings

Use the `settings_production.py` file for production deployment. It includes:
- Security headers (HSTS, SSL redirect, secure cookies)
- Proper logging configuration
- Production-ready email backend
- Database connection pooling

## Pre-deployment Checklist

- [ ] Set DEBUG=False
- [ ] Generate secure SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up PostgreSQL database
- [ ] Configure email backend
- [ ] Test all migrations
- [ ] Collect static files
- [ ] Test payment flow
- [ ] Verify email functionality
- [ ] Check admin analytics
- [ ] Test seat booking timeout
- [ ] Verify trailer embedding

## Database Migration

For production, you'll need to migrate from SQLite to PostgreSQL:

1. Export data from SQLite (if needed)
2. Set up PostgreSQL database
3. Run migrations: `python manage.py migrate --settings=bookmyseat.settings_production`
4. Create superuser: `python manage.py createsuperuser --settings=bookmyseat.settings_production`

## Static Files

Make sure to collect static files before deployment:
```bash
python manage.py collectstatic --settings=bookmyseat.settings_production
```

## Monitoring

The production settings include logging configuration that will:
- Log errors to `django_errors.log`
- Log to console for containerized deployments
- Use verbose formatting for better debugging

## Security Notes

- Never expose your SECRET_KEY
- Always use HTTPS in production
- Configure proper CORS headers if needed
- Set up rate limiting for API endpoints
- Use environment variables for sensitive data