# syntax=docker/dockerfile:1
FROM python:3  as ngen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN ls -l
RUN pip install -r requirements.txt
#COPY ../ /code/