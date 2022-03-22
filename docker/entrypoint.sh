#!/bin/sh
python manage.py makemessages -l es -i venv --no-location
python manage.py compilemessages -l es -i venv
python manage.py migrate --noinput
python manage.py createsuperuser --noinput --username ngen
python manage.py collectstatic -c --noinput
exec "$@"