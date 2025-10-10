from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class ChatUser(AbstractUser):
    email = models.EmailField("Электронная почта", unique=True)
    phone = models.CharField("Телефон")
    country_code = models.CharField("Код страны")
    code = models.IntegerField("Код подтверждения", default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'country_code']

    def __str__(self):
        return self.username


class Chat(models.Model):
    user_id_1 = models.IntegerField()
    user_id_2 = models.IntegerField()

    def __str__(self):
        return f"Chat between {self.user_id_1} and {self.user_id_2}"


class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField("Название")


class ChannelMembership(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name='id_user')
    chanel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='chanel_id')


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField("Текст")
    image = models.ImageField(upload_to='messages/images/', null=True, blank=True)
    video = models.FileField(upload_to='messages/videos/', null=True, blank=True)
    audio = models.FileField(upload_to='messages/audios/', null=True, blank=True)
    timestamp = models.DateTimeField("Дата", auto_now=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} in chat {self.chat.id}"
