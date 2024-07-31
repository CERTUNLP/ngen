FROM python:alpine as ngen-django
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apk add gettext libmagic gcc musl-dev python3-dev

ARG REACT_APP_NGEN_LANG 
ENV REACT_APP_NGEN_LANG $REACT_APP_NGEN_LANG

COPY . /code/
RUN pip install -r requirements.txt
