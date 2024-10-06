#!/bin/bash

# Exit the script on any error
set -e

# Wait for PostgreSQL service to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

# Apply database migrations for all apps
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the appropriate server based on the environment
if [ "$DJANGO_DEBUG" = "True" ]; then
    echo "Starting Django development server..."
    python manage.py runserver 0.0.0.0:8001
else
    echo "Starting Daphne server..."
    daphne -b 0.0.0.0 -p 8001 Caboo_backend.asgi:application &
    celery -A Caboo_backend worker --loglevel=info --pool=solo

fi