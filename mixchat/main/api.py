from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Message, Chat, Channel, ChannelMembership
from .serialazers import (UserSerializer, LoginSerializer, SendMessageSerializer, SearchUserSerializer,
                          GetOneChatSerializer, GetChatsSerializer, MessageSerializer,
                          CreateChatSerializer, CreateChannelSerializer,
                          SubscribeToChannelSerializer, SendMessageToChannelSerializer)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': int(user.id),
            'redirect_url': '/chat',  # URL для перенаправления на страницу почты
        })


class SendMessageView(generics.GenericAPIView):
    serializer_class = SendMessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_id = request.user.id
        recipient_id = serializer.validated_data['recipient_id']
        content = serializer.validated_data['content']
        chat_id = serializer.validated_data['chat_id']
        print('ЧАТТТТТ', chat_id)
        message = Message.objects.create(sender_id=sender_id, recipient_id=recipient_id, content=content, chat_id=chat_id)
        return Response({
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'content': content
        })


class SearchUserView(generics.GenericAPIView):
    serializer_class = SearchUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = User.objects.all()
        return Response({
            'users': [{
                "id": user.id,
                "username": user.username,
                "email": user.email
            } for user in users]
        })


class GetOneChatView(generics.GenericAPIView):
    serializer_class = GetOneChatSerializer
    authentication_classes = [JWTAuthentication]
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


class GetChatsView(generics.GenericAPIView):
    serializer_class = GetChatsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chats = Chat.objects.all()
        users = User.objects.all()
        chat_with_user = []
        for user, chat in zip(users, chats):
            chat_with_user.append({
                "id": chat.id,
                "user_id_1": chat.user_id_1,
                "user_id_2": chat.user_id_2,
                "username": user.username
            })
        return Response({
            'chats': chat_with_user
        })


class GreateChatView(generics.GenericAPIView):
    serializer_class = CreateChatSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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


class MessageView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        chat_id = request.GET.get('chat_id')
        messages = Message.objects.filter(chat_id=chat_id).order_by('timestamp')
        return Response({
            'messages': [{
                "id": message.id,
                "sender_id": str(message.sender),
                "recipient_id": str(message.recipient),
                "content": message.content,
                "date": message.timestamp
            } for message in messages]
        })


class GreateChannelView(generics.GenericAPIView):
    serializer_class = CreateChannelSerializer
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
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