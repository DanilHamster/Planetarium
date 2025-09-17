FROM python:3.12-alpine3.22

LABEL maintainer="dtaranenko137@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt


RUN apk add --no-cache postgresql-client

COPY . .


RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user



USER django-user

## 🧱 Визначаємо базовий образ Python
#FROM python:3.11-slim
#
## 🔧 Задаємо змінні середовища
#ENV PYTHONDONTWRITEBYTECODE=1 \
#    PYTHONUNBUFFERED=1
#
## 📁 Встановлюємо робочу директорію
#WORKDIR /app
#
## 📦 Копіюємо файл залежностей та встановлюємо їх
#COPY requirements.txt .
#RUN pip install --upgrade pip && pip install -r requirements.txt
#
## 📂 Копіюємо весь проєкт у контейнер
#COPY . .
#
## 🚀 Запускаємо Django-сервер
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#3.docker build -t name .
#4.docker run -p 8001:8000 name