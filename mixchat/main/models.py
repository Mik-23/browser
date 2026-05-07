import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class ChatUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    nickname = models.URLField("Никнейм", unique=True)
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

    def __str__(self):
        return self.name


class Chat(models.Model):
    name = models.TextField("Название чата")
    photo = models.ImageField(upload_to='photo/profilephoto/', default='photo/profilephoto/default.png', null=True,
                              blank=True, verbose_name="Фотография чата")
    bio = models.TextField("Описание")
    type = models.TextField("Тип")


class ChatMembership(models.Model):
    user_id = models.UUIDField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='id_chat')
    user_role = models.TextField("Роль пользователя")

    def __str__(self):
        return f"Membership of chat{self.chat}"


class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField("Название")
    photo = models.ImageField(upload_to='photo/profilephoto/', default='photo/profilephoto/default.png', null=True,
                              blank=True, verbose_name="Фотография канала")
    bio = models.TextField("Описание")


class ChannelMembership(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, related_name='id_user')
    chanel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='chanel_id')
    user_role = models.TextField("Роль пользователя")


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    sender_user = models.ForeignKey(ChatUser, verbose_name="Пользователь отправитель", null=True, blank=True, on_delete=models.CASCADE, related_name='sent_messages')
    sender_bot = models.ForeignKey(Bot, verbose_name="Бот отправитель", null=True, blank=True, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.TextField("Тип")
    content = models.TextField("Текст")
    image = models.ImageField("Картинка", upload_to='messages/images/', null=True, blank=True)
    video = models.FileField("Видео", upload_to='messages/videos/', null=True, blank=True)
    audio = models.FileField("Аудио", upload_to='messages/audios/', null=True, blank=True)
    timestamp = models.DateTimeField("Дата", auto_now_add =True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    is_edit = models.BooleanField("Редактировано?", null=True, blank=True)
    answer_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    is_forwarded = models.BooleanField("Пересылка?", null=True)

    def __str__(self):
        return f"Message from {self.sender_user} to chat {self.chat.id}"


class MessageHistory(models.Model):
    old_message = models.TextField("Старое сообщение")
    new_message = models.TextField("Новое сообщение")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='message_history')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='edit_chat_messages')
    old_date = models.DateTimeField("Старая дата")
    new_date = models.DateTimeField("Новая дата", auto_now_add =True)
    edited = models.ForeignKey(ChatUser, verbose_name="Отредактировал", null=True, blank=True, on_delete=models.CASCADE, related_name='edited_user')


class DeletedMessage(models.Model):
    delete_type = models.TextField("Тип удаления")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='message_deleted')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='delete_chat_messages')
    delete_date = models.DateTimeField("Дата удаления", auto_now_add =True)
    deleted = models.ForeignKey(ChatUser, verbose_name="Удалил", null=True, blank=True, on_delete=models.CASCADE, related_name='deleted_user')


class ChannelMessage(models.Model):
    id = models.AutoField(primary_key=True)
    message_type = models.TextField("Тип")
    content = models.TextField("Текст")
    image = models.ImageField("Картинка", upload_to='messages/images/', null=True, blank=True)
    video = models.FileField("Видео", upload_to='messages/videos/', null=True, blank=True)
    audio = models.FileField("Аудио", upload_to='messages/audios/', null=True, blank=True)
    timestamp = models.DateTimeField("Дата", auto_now_add =True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_messages')
    is_edit = models.BooleanField("Редактировано?", null=True, blank=True)
    answer_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    is_forwarded = models.BooleanField("Переслано?", null=True)


class ChannelChat(models.Model):
    channel_message = models.ForeignKey(ChannelMessage, on_delete=models.CASCADE, related_name='message_channel')


class AnswerChannelMessage(ChannelMessage):
    sender_user = models.ForeignKey(ChatUser, verbose_name="Пользователь отправитель", null=True, blank=True, on_delete=models.CASCADE, related_name='sent_channel_messages')
    channel_chat = models.ForeignKey(ChannelChat, on_delete=models.CASCADE, related_name='message_channel')
