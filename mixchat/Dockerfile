FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE='porno_chrome.settings'

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate
