#!/bin/sh

python manage.py migrate
python manage.py populate_history --auto
python manage.py runserver 0.0.0.0:8000
