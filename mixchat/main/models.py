import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class ChatUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    email = models.EmailField("Электронная почта", unique=True)
    phone = models.CharField("Телефон")
    country_code = models.CharField("Код страны")
    code = models.IntegerField("Код подтверждения", default=0)
    photo = models.ImageField(upload_to='photo/profilephoto/', default='photo/profilephoto/default.png', null=False, blank=True, verbose_name="Фотография")
    date_birth = models.DateField(null=True, blank=True)
    bio = models.CharField(null=True, blank=True)
    fcm_token = models.CharField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'country_code']

    def __str__(self):
        return self.username


class Bot(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    name = models.TextField("Имя")
    photo = models.ImageField(upload_to='photo/profilephoto/', default='photo/profilephoto/default.png', null=False,
                              blank=True, verbose_name="Фотография")


class Chat(models.Model):
    user_id_1 = models.TextField()
    user_id_2 = models.TextField()
    type = models.TextField("Тип")

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
    sender = models.ForeignKey(ChatUser, verbose_name="Имя отправителя", on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(ChatUser, verbose_name="Имя получателя", on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField("Текст")
    image = models.ImageField("Картинка", upload_to='messages/images/', null=True, blank=True)
    video = models.FileField("Видео", upload_to='messages/videos/', null=True, blank=True)
    audio = models.FileField("Аудио", upload_to='messages/audios/', null=True, blank=True)
    timestamp = models.DateTimeField("Дата", auto_now=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} in chat {self.chat.id}"


class MessageBot(models.Model):
    id = models.AutoField(primary_key=True)
    sender_id = models.TextField()
    bot_id = models.TextField()
    sender = models.TextField("Имя пользователя")
    bot = models.TextField("Название бота")
    content = models.TextField("Текст")
    image = models.ImageField(upload_to='messages/images/', null=True, blank=True)
    timestamp = models.DateTimeField("Дата", auto_now=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages_bot')
