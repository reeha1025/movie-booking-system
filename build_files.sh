#!/bin/bash

echo "Building Django application for production..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --settings=bookmyseat.settings_production

# Run migrations
python manage.py migrate --settings=bookmyseat.settings_production

echo "Build completed successfully!"