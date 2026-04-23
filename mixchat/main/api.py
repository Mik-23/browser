import os
import json
import random
from dotenv import load_dotenv
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views import View
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
from .cifer import gen_key, encrypt_text, decrypt_text
from .models import Message, Chat, Channel, ChannelMembership, ChatUser, Bot, ChatMembership
from .serialazers import (send_code_to_email, UserSerializer, SendCodeSerializer, LoginSerializer, MessageSerializer,
                          SearchUserSerializer,ChatSerializer, GetChatsSerializer, AnswerAndTransmissionSerializer,
                          CreateChannelSerializer, SubscribeToChannelSerializer,
                          SendMessageToChannelSerializer, ProfileformSerializer)


load_dotenv()
salt = os.getenv('CIFER_SALT')


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


class ResendCodeView(generics.GenericAPIView):
    # Повторная отправка кода
    def put(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if not email:
            return Response({"error": "Email обязателен!"})
        user = ChatUser.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Такого пользователя не существует."})
        code = random.randint(1000, 9999)
        user.code = code
        user.save()
        send_code_to_email(user.email, user.username, code)
        return Response({"message": "Ваш код был отправлен повторно."})


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
            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'redirect_url': '/',  # URL для перенаправления на страницу почты
            })
            response.set_cookie(
                'media_token',
                refresh.access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=30 * 60
            )
            return response
        except AttributeError:
            return Response({'error': 'Неверный логин или пароль'})


class LogoutView(APIView):
    # Выход из системы
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Successfully logged out.",
                         'logout_redirect': '/auth_in_chat'})
        response.delete_cookie('media_token')
        response.delete_cookie('refresh_token')
        return response


class ProfileformView(generics.GenericAPIView):
    # API профиля
    serializer_class = ProfileformSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]

    def get(self, request):
        # Открыть профиль пользователя
        user_id = request.GET.get('user_id')
        user = ChatUser.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "Ошибка. Такого пользователя не существует"})
        # Собираем список чатов с текущим пользователем
        member = [chat.chat_id for chat in ChatMembership.objects.filter(user_id=request.user.id)]
        # Проверяем, существует ли чат текущего пользователя и выбранного
        is_member = ChatMembership.objects.filter(
            chat_id__in=member,
            user_id=user_id
        ).exists()
        if not is_member:
            return Response({"error": "Невозможно просмотреть профиль, если отсутствует чат."})
        else:
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


class LoadMediaView(View):
    # API для загрузки медиа
    def get(self, request, file_name):
        # Создаём словарь с типами медиафайлов
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml',
            'mp4': 'video/mp4',
            'mov': 'video/quicktime',
            'avi': 'video/x-msvideo',
            'mkv': 'video/x-matroska',
            'webm': 'audio/webm',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac',
            'm4a': 'audio/mp4',
        }
        print("=== ВСЕ КУКИ, КОТОРЫЕ ВИДИТ СЕРВЕР ===")
        print(request.COOKIES)
        print(request.user)
        print("=====================================")
        # Если это фото для пользователей или чатов
        if file_name.startswith('photo'):
            user = ChatUser.objects.filter(photo=file_name).first()
            # Если пользователь с фото найден
            if user:
                # Открываем фото профиля
                with open(user.photo.path, 'rb') as f:
                    data = f.read()
                    return HttpResponse(data, content_type='image/jpeg')
            else:
                chat = Chat.objects.filter(photo=file_name).first()
                # Открываем фото чата
                with open(chat.photo.path, 'rb') as f:
                    data = f.read()
                    return HttpResponse(data, content_type='image/jpeg')
        # Находим тип выбранного файла
        file_type = file_name[file_name.rindex('.'):]
        message = None
        content_type = None
        media_file = None
        for key, value in mime_types.items():
            if key == file_type[1:] and value[0:value.index('/')] == 'image':
                # Задаём тип фото
                message = Message.objects.filter(image=file_name).first()
                content_type = value
                media_file = message.image.path
            elif key == file_type[1:] and value[0:value.index('/')] == 'video':
                # Задаём тип видео
                message = Message.objects.filter(video=file_name).first()
                content_type = value
                media_file = message.video.path
            elif key == file_type[1:] and value[0:value.index('/')] == 'audio':
                # Задаём тип аудио
                message = Message.objects.filter(audio=file_name).first()
                content_type = value
                media_file = message.audio.path
        chat = Chat.objects.filter(id=message.chat_id).first()
        members = ChatMembership.objects.filter(chat_id=chat.id).all()
        members = list(map(lambda x: x.user_id, members))
        if request.user.id in members:
            with open(media_file, 'rb') as f:
                data = f.read()
                return HttpResponse(data, content_type=content_type)
        else:
            return HttpResponse("Ошибка. Пользователя нет в чате.")


class MessageView(generics.GenericAPIView):
    # API сообщений
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Отправить сообщение
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Получаем текущего пользователя
        sender_id = request.user.id
        # Получаем отправителя
        content = serializer.validated_data['content']
        chat_id = serializer.validated_data['chat_id']
        member = ChatMembership.objects.filter(user_id=sender_id, chat_id=chat_id)
        if not member:
            return Response({"error": "Ошибка. Невозможно отправлять сообщения, где вас нет в чате"})
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response({"error": "Чат не найден"})
        chat_type = chat.type
        # type = serializer.validated_data['type']
        # Получаем файлы фото, видео и аудио
        image_file = request.FILES.get('image')
        video_file = request.FILES.get('video')
        audio_file = request.FILES.get('audio')
        key = gen_key(chat_id, salt)
        if chat_type == 'user' or chat_type == 'group':
            message = Message(
                sender_user_id=sender_id,
                content=encrypt_text(content, key),
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
            recipient = bot.name
            message = Message(
                sender_user_id=sender_id,
                content=encrypt_text(content, key),
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
                content=encrypt_text(message_content, key),
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
        key = gen_key(chat_id, salt)
        member = ChatMembership.objects.filter(user_id=request.user.id, chat_id=chat_id)
        if not member:
            return Response({"error": "Ошибка. Невозможно просматривать сообщения в чате, где вас нет"})
        messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
        list_messages = [{
                "id": message.id,
                "sender_user": str(message.sender_user),
                "sender_user_id": str(message.sender_user_id),
                "sender_bot": str(message.sender_bot),
                "sender_bot_id": str(message.sender_bot_id),
                "content": decrypt_text(message.content[2:-1].encode('utf-8'), key) if message.content else '',
                "image": message.image.url if message.image else None,
                "video": message.video.url if message.video else None,
                "audio": message.audio.url if message.audio else None,
                "date": message.timestamp.date(),
                "time": timezone.localtime(message.timestamp).strftime('%H:%M'),
                "chat_id": message.chat_id,
                "is_edit": message.is_edit,
                "delete_at_home": message.delete_at_home,
                "id_for_answer": message.id_for_answer,
                "is_forwarded": message.is_forwarded,
                "transmission_content": decrypt_text(message.transmission_content[2:-1].encode('utf-8'),
                                        gen_key(Message.objects.get(id=message.id_for_transmission).chat_id, salt)) if message.transmission_content else '',
                "id_for_transmission": message.id_for_transmission
            } for message in messages]
        return Response({
            'messages': list_messages
        })

    def put(self, request, *args, **kwargs):
        # Редактировать сообщение
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data['content']
        chat_id = serializer.validated_data['chat_id']
        message_id = serializer.validated_data['message_id']
        key = gen_key(chat_id, salt)
        member = ChatMembership.objects.filter(chat_id=chat_id, user_id=request.user.id)
        if not member:
            return Response({"error": "Ошибка. Невозможно редактировать сообщения, где вас нет в чате"})
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response({"error": "Чат не найден"})
        message = Message.objects.filter(id=message_id).first()
        if not message:
            return Response({"error": "Сообщение не найдено"})

        if message.sender_user_id != request.user.id:
            return Response({"error": "Вы можете редактировать только свои сообщения"})

        message.content = encrypt_text(content, key)
        message.is_edit = True
        message.save()
        return Response({
            'content': content,
            'image': message.image.url if message.image else None,
            'video': message.video.url if message.video else None,
            'audio': message.audio.url if message.audio else None,
            'message_id': message.id
        })

    def delete(self, request, *args, **kwargs):
        # Удалить сообщение
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_id = serializer.validated_data['chat_id']
        message_ids = serializer.validated_data['message_ids']
        delete_type = serializer.validated_data['delete_type']
        member = ChatMembership.objects.filter(chat_id=chat_id, user_id=request.user.id)
        if not member:
            return Response({"error": "Ошибка. Невозможно удалить сообщения, где вас нет в чате"})
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response({"error": "Чат не найден"})
        for message_id in message_ids:
            message = Message.objects.filter(id=message_id).first()
            if delete_type == 'Только у себя':
                message.delete_at_home = True
                message.save()
                return Response({'message': 'Вы удалили сообщение у себя.'})
            elif delete_type == 'У всех':
                message.delete()
                return Response({'message': 'Вы удалили сообщение у всех.'})
            else:
                return Response({'message': 'Ошибка. Не выбран тип удаления.'})


class AnswerMessageView(generics.GenericAPIView):
    serializer_class = AnswerAndTransmissionSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ответить на сообщение
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message_id = serializer.validated_data['message_id']
        chat_id = serializer.validated_data['chat_id']
        answer = serializer.validated_data['answer']
        key = gen_key(chat_id, salt)
        chat = Chat.objects.filter(id=chat_id).first()
        member = ChatMembership.objects.filter(chat_id=chat_id, user_id=request.user.id)
        if not member:
            return Response({"error": "Ошибка. Невозможно ответить на сообщение, где вас нет в чате"})
        if not chat:
            return Response({"error": "Чат не найден"})

        new_message = Message.objects.create(sender_user_id=request.user.id, content=encrypt_text(answer, key),
                                             id_for_answer=message_id, chat_id=chat_id)
        return Response({
            'answer': answer,
            'id_for_answer': new_message.id_for_answer
        })


class MessageTransmissionView(generics.GenericAPIView):
    serializer_class = AnswerAndTransmissionSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Переслать сообщение
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message_id = serializer.validated_data['message_id']
        chat_id = serializer.validated_data['chat_id']
        answer = serializer.validated_data['answer']
        to_chat_id = serializer.validated_data['to_chat_id']
        key = gen_key(to_chat_id, salt)
        current_chat = Chat.objects.filter(id=chat_id).first()
        to_chat = Chat.objects.filter(id=to_chat_id).first()
        message = Message.objects.filter(id=message_id).first()
        member = ChatMembership.objects.filter(chat_id=chat_id, user_id=request.user.id)
        if not member:
            return Response({"error": "Ошибка. Невозможно переслать сообщение из чата, где вас нет."})
        if not current_chat:
            return Response({"error": "Чат не найден"})
        if not to_chat:
            return Response({"error": "Чат для пересылки не найден"})
        new_message = Message.objects.create(sender_user_id=request.user.id, content=encrypt_text(answer, key),
                                             id_for_transmission=message_id, chat_id=to_chat_id,
                                             is_forwarded=True, transmission_content=message.content)
        return Response({
            'answer': answer,
            'id_for_transmission': new_message.id_for_transmission,
            'old_chat_id': chat_id,
            'to_chat_id': new_message.chat_id
        })


class MessageCountView(View):
    def get(self, request):
        chat_id = request.GET.get('chat_id')
        count = Message.objects.filter(chat_id=chat_id).count()

        return JsonResponse({'count': count})


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
        if not chat:
            return Response({"error": "Чат не найден"})
        if not chat.photo:
            photo = ''
        else:
            photo = chat.photo.url
        current_user_chat = [str(member.chat_id) for member in ChatMembership.objects.filter(user_id=request.user.id)]
        if str(chat_id) not in current_user_chat:
            return Response({"error": "Невозможно просматривать чаты в которых нет текущего пользователя"})
        memberships = ChatMembership.objects.filter(chat_id=chat.id).all()
        users_and_bots = list(ChatUser.objects.all())
        bots = list(Bot.objects.all())
        users_and_bots.extend(bots)
        users = []
        member_group = sorted([user for user in users_and_bots if user.id in [membership.user_id for membership in memberships]], key=lambda user: user.id)
        roles = [membership.user_role for membership in sorted(memberships, key=lambda member: member.user_id)]
        for member, role in zip(member_group, roles):
            if isinstance(member, ChatUser):
                users.append((member.username, member.photo.url, role))
            elif isinstance(member, Bot):
                users.append((member.name, member.photo.url, role))
        return Response({
            'id': chat.id,
            'name': chat.name,
            'bio': chat.bio,
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
        type_chat = serializer.validated_data['type']
        bio = serializer.validated_data['bio']
        try:
            users = serializer.validated_data['users']
        except KeyError:
            users = None
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response({"error": "Чат не найден"})
        # Проверяем: является ли чат групповым
        if type_chat == 'group':
            membership = ChatMembership.objects.filter(chat_id=chat_id, user_role='Создатель').first()
            if not membership:
                return Response({"error": "Участник чата не найден"})
            # Проверяем: является ли текущий пользователь создателем группы
            if membership.user_id == request.user.id and chat.type == type_chat:
                # Если да, то изменяем информацию о группе
                chat.name = name
                chat.bio = bio
                if users:
                    for user in users:
                        membership = ChatMembership.objects.filter(user_id=user, chat_id=chat.id).first()
                        if membership:
                            return Response({"error": "Такой пользователь уже существует в чате"})
                        else:
                            ChatMembership.objects.create(user_id=user, chat_id=chat.id)
                if photo != None:
                    chat.photo.save(photo.name, photo)
                chat.save()
                return Response({'message': 'Информация о группе изменилась.'})
            else:
                return Response({'message': 'Ошибка. Недостаточно прав для редактирования группы.'})
        else:
            return Response({'message': 'Ошибка. Возможно изменять только группы.'})


class DeleteUserFromGroup(generics.GenericAPIView):
    # Удаляем пользователя из группы
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        data = request.data
        membership = ChatMembership.objects.filter(chat_id=data['chat_id'], user_id=request.user.id, user_role='Создатель').first()
        if membership:
            membership = ChatMembership.objects.filter(chat_id=data['chat_id'], user_id=data['user_id'])
            membership.delete()
            return Response({'message': 'Пользователь был удалён из группы'})
        else:
            return Response({'message': 'Ошибка. Только создатель может удалить из группы'})


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
        for chat in list(set(chats_users)):
            message = Message.objects.filter(chat=chat.id).order_by('-timestamp').first()
            memberships = ChatMembership.objects.filter(chat_id=chat.id)
            memberships = memberships.exclude(user_id=request.user.id).all()
            if list(memberships) == []:
                user = ChatUser.objects.filter(id=request.user.id).first()
            else:
                user = ChatUser.objects.filter(id=memberships[0].user_id).first()
            key = gen_key(chat.id, salt)
            if message is not None:
                if message.content != '':
                    content = decrypt_text(message.content[2:-1].encode('utf-8'), key)
                else:
                    content = ''
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

            if user.photo is not None or user.photo == '':
                photo = user.photo.url
            else:
                photo = ''
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                print('Ошибка: Невозможно декодировать формат отличный от JSON')

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
                if message.image and not content:
                    content = 'Фотография'
            else:
                content = ''
                sender_name = ''
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
            key = gen_key(chat.id, salt)
            if len(content) == 0:
                content = ''
            else:
                content = decrypt_text(content[2:-1].encode('utf-8'), key)

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel_id = serializer.validated_data['channel_id']
        sender_id = serializer.validated_data['sender_id']
        content = serializer.validated_data['content']
        message = Message.objects.create(sender_id=sender_id, content=content)
        message.channel_id = channel_id
        return Response({
            'message': f'Сообщение отправлено в канал с id {channel_id}.'
        })
