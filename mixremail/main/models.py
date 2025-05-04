from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_id_for_message')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_id_for_message')
    content = models.TextField("Текст")
    timestamp = models.DateTimeField("Дата", auto_now=True)
    in_basket = models.BooleanField("В корзине")
    send_in_basket_id = models.IntegerField("Id сообщения в корзине")
    date_in_basket = models.DateTimeField("Дата отправки в корзину")


class Spam(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_id_for_spam')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_id_for_spam')
    content = models.TextField("Текст")
    timestamp = models.DateTimeField("Дата", auto_now=True)
    in_basket = models.BooleanField("В корзине")