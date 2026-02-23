FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE='mixchat.settings'

WORKDIR /mixchat

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip

RUN python manage.py collectstatic --noinput --verbosity 2

CMD ["sh", "-c", "python manage.py migrate"]
