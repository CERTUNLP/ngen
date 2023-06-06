#!/bin/sh

# python manage.py makemessages -l es -i venv --no-location
python manage.py compilemessages -l es -i venv
python manage.py migrate --noinput
python manage.py collectstatic -c --noinput
python manage.py  loaddata --app ngen priority feed tlp user taxonomy state edge report network_entity network contact
exec "$@"
