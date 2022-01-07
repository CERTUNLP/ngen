#!/bin/sh

python manage.py migrate --noinput
python manage.py createsuperuser --noinput --username ngen
exec "$@"