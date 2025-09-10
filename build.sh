#!/usr/bin/env bash
# build.sh - Render.com build script for Django Background Remover

set -o errexit  # exit on error

echo "Starting Render.com build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Creating superuser if needed..."
if [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

echo "Cleaning up old processed images..."
python manage.py cleanup_files

echo "Build completed successfully!"
