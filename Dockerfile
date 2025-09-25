FROM python:3.12-alpine3.22

LABEL maintainer="dtaranenko137@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN apk add --no-cache gcc musl-dev libpq postgresql-dev


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY . .


RUN adduser --disabled-password --no-create-home django-user
USER django-user
