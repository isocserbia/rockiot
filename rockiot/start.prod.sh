#!/bin/sh

export DEBUG=False
python manage.py migrate
python manage.py collectstatic
gunicorn -c python:project.gunicorn project.wsgi:application

