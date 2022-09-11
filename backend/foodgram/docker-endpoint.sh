#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata -i dump.json
python manage.py collectstatic --noinput
gunicorn foodgram.wsgi:application --bind 0:8000