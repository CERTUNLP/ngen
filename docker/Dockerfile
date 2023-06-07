# syntax=docker/dockerfile:1

FROM python:alpine as ngen-django
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apk add gettext libmagic gcc musl-dev python3-dev
COPY . /code/
RUN pip install -r requirements.txt
