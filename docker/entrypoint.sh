#!/bin/sh

if [ "$DJANGO_DEBUG" = "True" ]; then
    find . -name "*.mo" -delete
    python manage.py compilemessages -l es -i venv
fi
python manage.py migrate --noinput
python manage.py collectstatic -c --noinput
python manage.py loaddatafirsttime priority feed tlp user taxonomy state edge report_en report_es network_entity network contact playbook group
exec "$@"
