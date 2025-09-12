#!/bin/bash

# Railway startup script for Django Background Remover

echo "Starting Django Background Remover on Railway..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create media directories if they don't exist
echo "Creating media directories..."
mkdir -p media/uploads media/processed

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn bg_remover.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -
