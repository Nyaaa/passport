#!/bin/sh

echo "Applying migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Starting server"
uvicorn passport.asgi:application --host 0.0.0.0 --port "${PORT}"