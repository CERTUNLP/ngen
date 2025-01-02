FROM python:3.11.10-alpine3.20 AS ngen-django

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apk add gettext libmagic gcc musl-dev python3-dev

COPY . /code/

# Must be built from the project root directory
RUN pip install -r requirements.txt
