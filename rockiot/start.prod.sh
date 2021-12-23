#!/bin/sh

export DEBUG=False
python manage.py collectstatic
python manage.py migrate
#python manage.py populate_history --auto
gunicorn -c python:project.gunicorn project.wsgi:application
