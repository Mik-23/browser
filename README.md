MixRech вэбэкосистема с поисковиком MixRech и мессенджером MixChat.


Это два приложения, которые работают вместе. 
Поисковик ищет через Yandex API Search с помощью текста, фотографий и голоса. 
В мессенджере можно общаться, регистрироваться по почте (SMTP), а также в нём есть 2 системных бота:
1) MixRobot. Он выдаёт информацию из интернета через поисковик.
2) SmartMix. Он включает светодиод на микроконтроллере и показывает температуру с датчика DS18B20 через MQTT. 
Все данные сохраняются в PostgreSQL.


Технологии:                                                
Поисковая система — Django, Yandex Search API, SpeechKit, HTML, CSS, JavaScript.               
Мессенджер — Django REST Framework, REST API, Django ORM, JWT, SMTP, HTML, CSS, JavaScript.              
Сервер — Ubuntu, SSH, SSL, DNS, Docker, Docker Compose, Nginx, CI/CD (GitHub Actions).


Навигация:          
.github - CI/CD процесс,         
mixchat - мессенджер,             
mixrech - поисковик,                      
docker-compose.yml - файл с контейнерами поисковика, мессенджера и вэб-сервера,                        
nginx.conf - файл вэб-сервера.


<img width="1913" height="967" alt="mixrech_main_page" src="https://github.com/user-attachments/assets/965b749b-e17a-43f3-a0f5-b402e16169db" />
Рисунок 1 - Главная страница MixRech



<img width="1910" height="970" alt="mixchat_main_page" src="https://github.com/user-attachments/assets/6fa3fb39-9628-474d-8fc9-fce68517a39a" />
Рисунок 2 - Главная страница MixChat



<img width="1312" height="772" alt="mixrobot_job" src="https://github.com/user-attachments/assets/e80dea42-b9c6-4d06-a13f-1f4148d9bfb5" />
Рисунок 3 - Результат работы MixRobot


