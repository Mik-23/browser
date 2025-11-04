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
from .models import Message, Chat, Channel, ChannelMembership, ChatUser
from .serialazers import (UserSerializer, SendCodeSerializer, LoginSerializer, MessageSerializer,
                          SearchUserSerializer,ChatSerializer, GetChatsSerializer,
                          CreateChannelSerializer, SubscribeToChannelSerializer,
                          SendMessageToChannelSerializer)


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
            print('user', user)
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


class MessageView(generics.GenericAPIView):
    # Отправить сообщение
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
        print('ID чата', chat_id)
        # Получаем файлы фото, видео и аудио
        image_file = request.FILES.get('image')
        video_file = request.FILES.get('video')
        audio_file = request.FILES.get('audio')
        print('VIDEO', video_file)
        message = Message(
            sender_id=sender_id,
            content=content,
            recipient_id=recipient_id,
            chat_id=chat_id
        )

        # Сохраняем фото в БД если оно есть
        if image_file:
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
        return HttpResponse({
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'content': content,
            'image': image_file,
            'video': video_file,
            'audio': audio_file,
            'message_id': message.id
        })

    def get(self, request, *args, **kwargs):
        chat_id = request.GET.get('chat_id')
        messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
        return Response({
            'messages': [{
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
                "time": message.timestamp.strftime('%H:%m')
            } for message in messages]
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
        return Response({
            'users': [{
                "id": user.id,
                "username": user.username,
                "email": user.email
            } for user in users]
        })


class ChatView(generics.GenericAPIView):
    # Открыть один чат
    serializer_class = ChatSerializer
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_id = serializer.validated_data['sender_id']
        recipient_id = serializer.validated_data['recipient_id']
        user_ids = sorted([sender_id, recipient_id])
        serializer.is_valid(raise_exception=True)
        chat = Chat.objects.create(user_id_1=user_ids[0], user_id_2=user_ids[1])
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
        print(chats)
        chat_with_user = []
        for user, chat in zip(users, sorted(chats, key=lambda user: user.user_id_2)):
            print(f'{user}      {chat}')
            message = Message.objects.filter(chat=chat.id).order_by('-timestamp').first()
            if chat.user_id_1 < request.user.id and chat.user_id_2 == request.user.id:
                user = ChatUser.objects.filter(id=chat.user_id_1).first()
            elif chat.user_id_1 == request.user.id and chat.user_id_2 > request.user.id:
                user = ChatUser.objects.filter(id=chat.user_id_2).first()
            elif chat.user_id_1 == chat.user_id_2 == request.user.id:
                user = ChatUser.objects.filter(id=chat.user_id_1).first()
            if message is not None:
                content = message.content
            else:
                content = ''
            chat_with_user.append({
                "id": chat.id,
                "user_id_1": chat.user_id_1,
                "user_id_2": chat.user_id_2,
                "username": user.username,
                "content": content
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

