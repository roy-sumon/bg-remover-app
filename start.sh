#!/bin/bash

# Railway startup script for Django Background Remover
set -e  # Exit on any error

echo "=== Starting Django Background Remover on Railway ==="

# Check required environment variables
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable not set"
    exit 1
fi

echo "Port: $PORT"
echo "Python version: $(python --version)"
echo "Django version: $(python -c 'import django; print(django.VERSION)')"

# Run database migrations
echo "=== Running database migrations ==="
python manage.py migrate --noinput || {
    echo "ERROR: Database migration failed"
    exit 1
}

# Create media directories if they don't exist
echo "=== Creating media directories ==="
mkdir -p media/uploads media/processed
ls -la media/

# Collect static files (in case not done in build)
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear || {
    echo "WARNING: Static files collection failed, continuing..."
}

# Start the application with Gunicorn
echo "=== Starting Gunicorn server ==="
echo "Gunicorn version: $(gunicorn --version)"

exec gunicorn bg_remover.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload
