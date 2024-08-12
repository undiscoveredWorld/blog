#!/usr/bin/env bash

python manage.py makemigrations
python manage.py sqlmigrate Auth 0001
python manage.py sqlmigrate Posts 0001
python manage.py migrate Auth 0001
python manage.py migrate Posts 0001
python manage.py runserver 0.0.0.0:8080