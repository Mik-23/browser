MixRech вэбэкосистема с поисковиком MixRech и мессенджером MixChat.


Это два приложения, которые работают вместе. 
Поисковик ищет через Yandex API Search с помощью текста, фотографий и голоса. 
В мессенджере можно общаться, регистрироваться по почте (SMTP), а также в нём есть 2 системных бота:
1) MixRobot. Он выдаёт информацию из интернета через поисковик
2) SmartMix. Он включает светодиод на микроконтроллере и показывает температуру с датчика DS18B20 через MQTT. 
Все данные сохраняются в PostgreSQL.

Технологии:
Поисковая система — Django, Yandex Search API, SpeechKit, HTML, CSS, JavaScript
Мессенджер — Django REST Framework, REST API, Django ORM, JWT, SMTP, HTML, CSS, JavaScript
Сервер — Ubuntu, SSH, SSL, DNS, Docker, Docker Compose, Nginx, CI/CD (GitHub Actions)

Навигация:
.github - CI/CD процесс
mixchat - мессенджер
mixrech - поисковик
docker-compose.yml - файл с контейнерами поисковика, мессенджера и вэб-сервера
nginx.conf - файл вэб-сервера
