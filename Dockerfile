FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE='mixrech.settings'

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip
RUN rm -rf /app/staticfiles && python manage.py collectstatic --noinput
