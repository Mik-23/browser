import json
import time
from django.utils import timezone
from django.http import StreamingHttpResponse
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.urls import reverse
from .firebase import send_push_notification
from .microservice_functions import mixrech, send_to_mqtt, get_mqtt
from .models import Message, Chat, Channel, ChannelMembership, ChatUser, Bot, ChatMembership
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
        print('Отправитель', sender_id)
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
        if chat_type == 'user' or chat_type == 'group':
            message = Message(
                sender_user_id=sender_id,
                content=content,
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
            membership = ChatMembership.objects.filter(chat_id=chat_id)
            membership = membership.exclude(user_id=sender_id).first()
            if membership:
                users = ChatUser.objects.filter(id=membership.user_id).all()
            else:
                users = ChatUser.objects.filter(id=sender_id).all()
            message.save()
            # Отправляем уведомление получателю
            print('1', message.sender_user.username)
            print('2', users)
            for user in users:
                if message.sender_user.username != user.username:
                    send_push_notification(user.fcm_token, message.sender_user.username, content, message.sender_user.photo.url)
            return Response({
                'sender_id': sender_id,
                'content': content,
                'image': message.image.url if message.image else None,
                'video': message.video.url if message.video else None,
                'audio': message.audio.url if message.audio else None,
                'message_id': message.id
            })
        elif chat_type == 'bot':
            user = ChatUser.objects.filter(id=sender_id).first()
            sender = user.username
            membership = ChatMembership.objects.filter(chat_id=chat_id)
            membership = membership.exclude(user_id=sender_id).first()
            bot = Bot.objects.filter(id=membership.user_id).first()
            print('ewewewew', bot)
            print(f'ewewewew {chat_id}      {chat_type}')
            recipient = bot.name
            message = Message(
                sender_user_id=sender_id,
                content=content,
                chat_id=chat_id
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
            message_bot = Message(
                sender_bot_id=bot.id,
                content=message_content,
                chat_id=chat_id,
            )
            message_bot.save()
            return Response({
                'sender_id': sender_id,
                'content': content,
                'image': image_file,
                'message_id': message.id
            })

    def get(self, request, *args, **kwargs):
        # Получение сообщений
        chat_id = request.GET.get('chat_id')
        messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
        list_messages = [{
                "id": message.id,
                "sender_user": str(message.sender_user),
                "sender_user_id": str(message.sender_user_id),
                "sender_bot": str(message.sender_bot),
                "sender_bot_id": str(message.sender_bot_id),
                "content": message.content,
                "image": message.image.url if message.image else None,
                "video": message.video.url if message.video else None,
                "audio": message.audio.url if message.audio else None,
                "date": message.timestamp.date(),
                "time": timezone.localtime(message.timestamp).strftime('%H:%M'),
            } for message in messages]
        return Response({
            'messages': list_messages
        })


class MessageSSEView(generics.GenericAPIView):
    # Server-Sent Events — получаем сообщения в реальном времени

    def get(self, request):
        user = request.user
        chat_id = request.GET.get('chat_id')

        def event_stream():

            while True:
                # Получаем новые сообщения из БД
                new_messages = Message.objects.filter(chat_id=chat_id)

                # Отправляем каждое сообщение
                for msg in new_messages:
                    data = {
                        'id': msg.id,
                        'from': msg.sender_user.username,
                        'text': msg.content,
                        'time': msg.timestamp.isoformat()
                    }
                    yield f"data: {json.dumps(data)}\n\n"


                # Если нет новых сообщений, отправляем keepalive
                # и ждем 1 секунду
                yield ": keepalive\n\n"
                time.sleep(1)  # ← простая задержка, ничего сложного

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        return response


class SaveFCMToken(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        user.fcm_token = data['token']
        user.save()
        return Response({
            'users': 'Успешно'
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
        # Показать пользователей в чате
        chat_id = request.GET.get('chat_id')
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat.photo:
            photo = ''
        else:
            photo = chat.photo.url
        memberships = ChatMembership.objects.filter(chat_id=chat.id).all()
        users_and_bots = list(ChatUser.objects.all())
        bots = list(Bot.objects.all())
        users_and_bots.extend(bots)
        users = []
        print(users_and_bots)
        member_group = sorted([user for user in users_and_bots if user.id in [membership.user_id for membership in memberships]], key=lambda user: user.id)
        print(member_group)
        roles = [membership.user_role for membership in sorted(memberships, key=lambda member: member.user_id)]
        print(roles)
        for member, role in zip(member_group, roles):
            if isinstance(member, ChatUser):
                users.append((member.username, member.photo.url, role))
            elif isinstance(member, Bot):
                users.append((member.name, member.photo.url, role))
        print(users)
        return Response({
            'id': chat.id,
            'name': chat.name,
            'photo': photo,
            'users': users
        })

    def post(self, request, *args, **kwargs):
        # Создать чат/группу
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data['name']
        photo = request.FILES.get('photo')
        users = serializer.validated_data['users']
        type = serializer.validated_data['type']
        bio = serializer.validated_data['bio']
        if users != []:
            chat = Chat.objects.create(name=name, type=type, bio=bio)
            if photo != None:
                chat.photo.save(photo.name, photo)
                photo = chat.photo.url
            for user in users:
                membership = ChatMembership.objects.create(user_id=user, chat_id=chat.id)
                if str(membership.user_id) == str(request.user.id) and type == 'group':
                    print('membership 2',membership)
                    membership.user_role = 'Создатель'
                    membership.save()
            return Response({
                'id': chat.id,
                'name': chat.name,
                'photo': photo,
                'bio': bio
            })
        else:
            return Response({
                'message': 'Ошибка. Невозможно создать чат без пользователей.'
            })

    def put(self, request, *args, **kwargs):
        # Редактировать чат (групповой)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_id = serializer.validated_data['chat_id']
        name = serializer.validated_data['name']
        photo = request.FILES.get('photo')
        type = serializer.validated_data['type']
        bio = serializer.validated_data['bio']
        chat = Chat.objects.filter(id=chat_id).first()
        membership = ChatMembership.objects.filter(chat_id=chat_id, user_role='Создатель').first()
        # Проверяем: является ли текущий пользователь создателем группы
        if membership.user_id == request.user.id and chat.type == type:
            # Если да, то изменяем информацию о группе
            chat.name = name
            chat.bio = bio
            if photo != None:
                chat.photo.save(photo.name, photo)
            chat.save()
            return Response({
                'message': 'Информация о группе изменилась.'
            })
        else:
            return Response({
                'message': 'Ошибка. Недостаточно прав для редактирования группы.'
            })


class GetChatsView(generics.GenericAPIView):
    # Показать все чаты
    serializer_class = GetChatsSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Создаём список чатов
        chats = []
        # Создаём список участников чатов с текущим пользователем
        memberships = ChatMembership.objects.filter(user_id=request.user.id).all()
        for membership in memberships:
            chat = Chat.objects.filter(id=membership.chat_id).first()
            # Добавляем чат с текущим пользователем в список
            chats.append(chat)
        bots = Bot.objects.all()
        chat_with_user = []
        chats_users = list(filter(lambda x: x.type == 'user', chats))
        print(f'chats {set(chats_users)}          {chats}')
        for chat in list(set(chats_users)):
            message = Message.objects.filter(chat=chat.id).order_by('-timestamp').first()
            memberships = ChatMembership.objects.filter(chat_id=chat.id)
            memberships = memberships.exclude(user_id=request.user.id).all()
            if list(memberships) == []:
                user = ChatUser.objects.filter(id=request.user.id).first()
            else:
                user = ChatUser.objects.filter(id=memberships[0].user_id).first()

            if message is not None:
                content = message.content
                sender_name = message.sender_user.username + ': '
                print('SENDER_NAME', type(message.sender_user))
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
                "username": user.username,
                "content": content,
                "photo": photo,
                "bio": chat.bio,
                "sender_name": sender_name,
                "type": chat.type
            })
        chats_bots = list(filter(lambda x: x.type == 'bot', chats))
        for bot, chat in zip(bots, chats_bots):
            message = Message.objects.filter(chat=chat.id).order_by('-timestamp').first()
            if message is not None:
                content = message.content
                sender_name = str(message.sender_bot) + ': '
                print('bot',type(message.sender_bot))
                print('SENDER_NAME', sender_name)
                if message.image and not content:
                    content = 'Фотография'
            else:
                content = ''
                sender_name = ''
            print('CONTENT', content)
            try:
                new_content = ''
                update_content = content.replace('"', '#')
                update_content = update_content.replace("'", '"')
                json_content = json.loads(update_content)

                if isinstance(json_content, dict):
                    for con in json_content:
                        new_content = new_content + con + ' '
                else:
                    new_content = str(json_content)
                content = new_content
            except json.JSONDecodeError as e:
                print(f'(BOTS)Ошибка: {e}')
            if bot.photo is not None or bot.photo == '':
                photo = bot.photo.url
            else:
                photo = ''
            chat_with_user.append({
                "id": chat.id,
                "username": bot.name,
                "content": content,
                "photo": photo,
                "bio": chat.bio,
                "sender_name": sender_name,
                "type": chat.type
            })
        group_chats = list(filter(lambda x: x.type == 'group', chats))
        for chat in group_chats:
            message = Message.objects.filter(chat=chat.id).order_by('-timestamp').first()
            if message is not None:
                content = message.content
                sender_name = message.sender_user.username + ': '
                if message.image and not content:
                    content = 'Фотография'
                if message.video and not content:
                    content = 'Видеозапись'
                if message.audio and not content:
                    content = 'Аудиозапись'
            else:
                content = ''
                sender_name = ''
            if chat.photo is not None or chat.photo == '':
                photo = chat.photo.url
            else:
                photo = ''
            chat_with_user.append({
                "id": chat.id,
                "username": chat.name,
                "content": content,
                "photo": photo,
                "bio": chat.bio,
                "sender_name": sender_name,
                "type": chat.type
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
