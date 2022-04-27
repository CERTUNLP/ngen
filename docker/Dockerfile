# syntax=docker/dockerfile:1
FROM python:3-alpine  as ngen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apk add gettext libmagic
COPY requirements.txt /code/
RUN pip install -r requirements.txt
# celery beat patch until version 2.3.0 arrives
RUN pip install django-timezone-field==4.2.3 python-crontab==2.3.4
RUN pip install django-celery-beat==2.2.1 --no-deps

#COPY ../ /code/