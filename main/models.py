from django.db import models

# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    login = models.TextField("Логин")
    password = models.TextField("Пароль")
    mail = models.TextField("Почта")