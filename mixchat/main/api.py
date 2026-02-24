import json
from datetime import datetime
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse
from .microservice_functions import mixrech, send_to_mqtt, get_mqtt
from .models import Message, Chat, Channel, ChannelMembership, ChatUser, Bot, MessageBot
from .serialazers import (UserSerializer, SendCodeSerializer, LoginSerializer, MessageSerializer,
                          SearchUserSerializer,ChatSerializer, GetChatsSerializer,
                          CreateChannelSerializer, SubscribeToChannelSerializer,
                          SendMessageToChannelSerializer, ProfileformSerializer)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Отключаем проверку CSRF
        return


class RegisterView(generics.CreateAPIView):
    # Регистрация пользователя
    queryset = ChatUser.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Возвращаем сообщение об успешной регистрации и URL для авторизации
        return Response({
            'login_url': request.build_absolute_uri(reverse('confirmation_code'))
        })


class SendCodeView(generics.GenericAPIView):
    # Отправка СМС с кодом
    serializer_class = SendCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        user = ChatUser.objects.filter(code=code).first()
        if user is not None:
            user.is_active = True
            user.save()
            return Response({
                'message': 'Пользователь успешно зарегистрирован.',
                'login_url': request.build_absolute_uri(reverse('successfully'))
            })
        else:
            return Response({
                'message': 'Неверный код, пожалуйста, повторите попытку.',
                'login_url': request.build_absolute_uri(reverse('confirmation_code'))
            })


class LoginView(generics.GenericAPIView):
    # Вход в систему
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = authenticate(username=email, password=password)
            print('user', type(user.id))
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'redirect_url': '/',  # URL для перенаправления на страницу почты
            })
        except AttributeError:
            return Response({'error': 'Неверный логин или пароль'})


class LogoutView(APIView):
    # Выход из системы
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Successfully logged out.",
                         'logout_redirect': '/auth_in_chat'})


class ProfileformView(generics.GenericAPIView):
    # API профиля
    serializer_class = ProfileformSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]

    def get(self, request):
        # Открыть профиль пользователя
        user_id = request.GET.get('user_id')
        user = ChatUser.objects.filter(id=user_id).first()
        return Response({"photo": user.photo.url,
                         "name": user.username,
                         'date_birth': user.date_birth,
                         'bio': user.bio})

    def put(self, request, *args, **kwargs):
        # Редактировать профиль пользователя
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = request.FILES.get('photo')
        name = serializer.validated_data['name']
        date_birth = serializer.validated_data['date_birth']
        bio = serializer.validated_data['bio']
        user = ChatUser.objects.filter(id=request.user.id).first()
        user.username = name
        user.date_birth = date_birth
        user.bio = bio
        if photo != None:
            user.photo.save(photo.name, photo)
        user.save()
        return Response({"photo": user.photo.url,
                         'date_birth': user.date_birth})


class MessageView(generics.GenericAPIView):
    # API сообщений
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Отправить сообщение
        print(request.user.id)
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        # Получаем текущего пользователя
        sender_id = request.user.id
        # Получаем отправителя
        recipient_id = serializer.validated_data['recipient_id']
        print('Отправитель', sender_id)
        print('Получатель', recipient_id)
        content = serializer.validated_data['content']
        chat_id = serializer.validated_data['chat_id']
        chat = Chat.objects.filter(id=chat_id).first()
        chat_type = chat.type
        # type = serializer.validated_data['type']
        print('ID чата', chat_id)
        # Получаем файлы фото, видео и аудио
        image_file = request.FILES.get('image')
        video_file = request.FILES.get('video')
        audio_file = request.FILES.get('audio')
        print('VIDEO', video_file)
        if chat_type == 'user':
            message = Message(
                sender_id=sender_id,
                content=content,
                recipient_id=recipient_id,
                chat_id=chat_id
            )

            # Сохраняем фото в БД если оно есть
            if image_file != None:
                message.image.save(image_file.name, image_file)
            else:
                message.image = None

            # Сохраняем видео в БД если оно есть
            if video_file:
                message.video.save(video_file.name, video_file)
            else:
                message.video = None

            # Сохраняем аудио в БД если оно есть
            if audio_file:
                message.audio.save(audio_file.name, audio_file)
            else:
                message.audio = None

            message.save()
            print(message.recipient)
            print('image', message.image.url if message.image else None)
            print('video', message.video.url if message.video else None)
            print('audio', message.audio.url if message.audio else None)
            return Response({
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'content': content,
                'image': message.image.url if message.image else None,
                'video': message.video.url if message.video else None,
                'audio': message.audio.url if message.audio else None,
                'message_id': message.id
            })
        elif chat_type == 'bot':
            user = ChatUser.objects.filter(id=sender_id).first()
            sender = user.username
            bot = Bot.objects.filter(id=recipient_id).first()
            recipient = bot.name
            message = MessageBot(
                sender_id=sender_id,
                content=content,
                bot_id=recipient_id,
                chat_id=chat_id,
                sender=sender,
                bot=recipient
            )

            # Сохраняем фото в БД если оно есть
            if image_file:
                message.image.save(image_file.name, image_file)
            else:
                message.image = None

            message.save()
            message_content = ''
            if recipient == 'Mixrobot':
                message_content = mixrech(content)
            elif recipient == 'SmartMix':
                send_to_mqtt(content)
                message_content = get_mqtt()
            message_bot = MessageBot(
                sender_id=recipient_id,
                content=message_content,
                bot_id=sender_id,
                chat_id=chat_id,
                sender=recipient,
                bot=sender
            )
            message_bot.save()
            return Response({
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'content': content,
                'image': image_file,
                'message_id': message.id
            })

    def get(self, request, *args, **kwargs):
        # Получение сообщений
        chat_id = request.GET.get('chat_id')
        print('hgfhfhfhf',chat_id)
        messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
        messages_bot = MessageBot.objects.filter(chat_id=chat_id).order_by('timestamp')
        list_messages = [{
                "id": message.id,
                "sender": str(message.sender),
                "recipient": str(message.recipient),
                "sender_id": str(message.sender_id),
                "recipient_id": str(message.recipient_id),
                "content": message.content,
                "image": message.image.url if message.image else None,
                "video": message.video.url if message.video else None,
                "audio": message.audio.url if message.audio else None,
                "date": message.timestamp.date(),
                "time": message.timestamp.strftime('%H:%m'),
            } for message in messages]
        list_messages_bot = [{
                "id": message.id,
                "sender": str(message.sender),
                "recipient": str(message.bot),
                "sender_id": str(message.sender_id),
                "recipient_id": str(message.bot_id),
                "content": message.content,
                "image": message.image.url if message.image else None,
                "date": message.timestamp.date(),
                "time": message.timestamp.strftime('%H:%m')
            } for message in messages_bot]
        print(list_messages_bot)
        list_messages.extend(list_messages_bot)
        return Response({
            'messages': list_messages
        })


class SearchUserView(generics.GenericAPIView):
    # Поиск по пользователю
    serializer_class = SearchUserSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = ChatUser.objects.all()
        bots = Bot.objects.all()
        list_users = [{"id": user.id, "username": user.username, "type": "user", "photo": user.photo.url} for user in users]
        list_bots = [{"id": bot.id, "username": bot.name, "type": "bot", "photo": bot.photo.url} for bot in bots]
        list_users.extend(list_bots)
        return Response({
            'users': list_users
        })


class GetCurrentUserView(generics.GenericAPIView):
    # Получить текущего пользователя
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = ChatUser.objects.filter(id=request.user.id).first()
        return Response({
            'name': user.username,
            'photo': user.photo.url,
            'date_birth': user.date_birth,
            'bio': user.bio
        })


class ChatView(generics.GenericAPIView):
    # API чатов
    serializer_class = ChatSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Открыть один чат
        sender_id = request.GET.get('sender_id')
        recipient_id = request.GET.get('recipient_id')

        # Упорядочиваем ID пользователей
        user_ids = sorted([sender_id, recipient_id])
        # Логика для поиска существующего чата
        chat = Chat.objects.filter(
            user_id_1=user_ids[0],
            user_id_2=user_ids[1]
        ).first()

        if chat:
            return Response({'chat_id': chat.id})  # Возвращаем ID существующего чата
        else:
            return Response({'chat_id': None})

    def post(self, request, *args, **kwargs):
        # Создать чат
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_id = serializer.validated_data['sender_id']
        recipient_id = serializer.validated_data['recipient_id']
        type = serializer.validated_data['type']
        user_ids = sorted([sender_id, recipient_id])
        serializer.is_valid(raise_exception=True)
        chat = Chat.objects.create(user_id_1=user_ids[0], user_id_2=user_ids[1], type=type)
        return Response({
            'id': chat.id,
            'user_id_1': chat.user_id_1,
            'user_id_2': chat.user_id_2
        })


class GetChatsView(generics.GenericAPIView):
    # Показать все чаты
    serializer_class = GetChatsSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Выбираем список чатов, где есть текущий пользователь
        chats = Chat.objects.filter(
            Q(user_id_1=request.user.id) |
            Q(user_id_2=request.user.id))
        users = ChatUser.objects.all()
        bots = Bot.objects.all()
        chat_with_user = []
        chats_users = list(filter(lambda x: x.type == 'user', chats))
        for user, chat in zip(users, sorted(chats_users, key=lambda user: user.user_id_2)):
            print(f'{user}      {chat}')
            message = Message.objects.filter(chat=chat.id).order_by('-timestamp').first()
            print(chat.user_id_1)
            print('Auth User', request.user.id)
            if chat.user_id_1 < str(request.user.id) and chat.user_id_2 == str(request.user.id):
                user = ChatUser.objects.filter(id=chat.user_id_1).first()
                print('Condition 1', user)
            elif chat.user_id_1 == str(request.user.id) and chat.user_id_2 > str(request.user.id):
                user = ChatUser.objects.filter(id=chat.user_id_2).first()
                print('Condition 2', user)
            elif chat.user_id_1 == chat.user_id_2 == str(request.user.id):
                user = ChatUser.objects.filter(id=chat.user_id_1).first()
                print('Condition 3', user)
            if message is not None:
                content = message.content
                sender_name = message.sender.username + ': '
                print('SENDER_NAME', type(message.sender))
                print('SENDER_NAME', sender_name)
                if message.image and not content:
                    content = 'Фотография'
                if message.video and not content:
                    content = 'Видеозапись'
                if message.audio and not content:
                    content = 'Аудиозапись'
            else:
                content = ''
                sender_name = ''

            if user.photo is not None or user.photo == '':
                photo = user.photo.url
            else:
                photo = ''
            print('PHOTO', photo)
            print('CONTENT 1', content)
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                print('Ошибка: Невозможно декодировать формат отличный от JSON')

            print('CONTENT', content)
            chat_with_user.append({
                "id": chat.id,
                "user_id_1": chat.user_id_1,
                "user_id_2": chat.user_id_2,
                "username": user.username,
                "content": content,
                "photo": photo,
                "sender_name": sender_name
            })
        chats_bots = list(filter(lambda x: x.type == 'bot', chats))
        for bot, chat in zip(bots, chats_bots):
            message = MessageBot.objects.filter(chat=chat.id).order_by('-timestamp').first()
            if message is not None:
                content = message.content
                sender_name = message.sender + ': '
                print('bot',type(message.sender))
                print('SENDER_NAME', sender_name)
                if message.image and not content:
                    content = 'Фотография'
            else:
                content = ''
                sender_name = ''
            print('CONTENT', content)
            try:
                new_content = ''
                update_content = content.replace("'", '"')
                json_content = json.loads(update_content)
                if isinstance(json_content, dict):
                    for con in json_content:
                        new_content = new_content + con + ' '
                else:
                    new_content = str(json_content)
                content = new_content
            except json.JSONDecodeError:
                print('(BOTS)Ошибка: Невозможно декодировать формат отличный от JSON')
            if bot.photo is not None or bot.photo == '':
                photo = bot.photo.url
            else:
                photo = ''
            chat_with_user.append({
                "id": chat.id,
                "user_id_1": chat.user_id_1,
                "user_id_2": chat.user_id_2,
                "username": bot.name,
                "content": content,
                "photo": photo,
                "sender_name": sender_name
            })
        return Response({
            'chats': chat_with_user
        })


class GreateChannelView(generics.GenericAPIView):
    serializer_class = CreateChannelSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data['name']
        channel = Channel.objects.create(name=name)
        return Response({
            'message': f'Канал с именем {name} создан'
        })


class SubscribeToChannelView(generics.GenericAPIView):
    serializer_class = SubscribeToChannelSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        channel_id = serializer.validated_data['channel_id']
        membership = ChannelMembership.objects.create(user_id=user_id, channel_id=channel_id)
        return Response({
            'message': f'Пользователь с id {user_id} подписался на канал с id {channel_id}.'
        })


class SendMessageToChannelView(generics.GenericAPIView):
    serializer_class = SendMessageToChannelSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.GET.get('sender_id'))
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        channel_id = serializer.validated_data['channel_id']
        sender_id = serializer.validated_data['sender_id']
        content = serializer.validated_data['content']
        message = Message.objects.create(sender_id=sender_id, content=content)
        message.channel_id = channel_id
        return Response({
            'message': f'Сообщение отправлено в канал с id {channel_id}.'
        })
