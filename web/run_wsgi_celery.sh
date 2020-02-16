#!/bin/bash
chmod 777 /tmp
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
celery worker -A mts_django --beat -l DEBUG -f /tmp/celery.log &
gunicorn -c /etc/gunicorn/gunicorn.py mts_django.wsgi:application
