FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Запускаем Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "porno_chrome.wsgi:application"]
