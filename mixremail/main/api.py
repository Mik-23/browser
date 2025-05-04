from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Message
from .serialazers import (UserSerializer, LoginSerializer, SendMessageSerializer,
                          GetSendMessageSerializer, GetRecipientMessageSerializer,
                          SendInBasketSerializer, GetBasketSerializer)


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
            'redirect_url': '/mail',  # URL для перенаправления на страницу почты
        })


class SendMessageView(generics.GenericAPIView):
    serializer_class = SendMessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.GET.get('sender_id'))
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        sender_id = request.user.id
        recipient_id = serializer.validated_data['recipient_id']
        content = serializer.validated_data['content']
        message = Message.objects.create(sender_id=sender_id, recipient_id=recipient_id, content=content)
        return Response({
            'sender_id': sender_id,
            'recipient_id': recipient_id,
            'content': content
        })


class GetSendMessageView(generics.GenericAPIView):
    serializer_class = GetSendMessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_id = request.user.id
        messages = Message.objects.filter(sender_id=sender_id).all()
        sender_messages = []
        for message in messages:
            sender_messages.append({
                "id": message.id,
                "sender_id": str(message.sender),
                "recipient_id": str(message.recipient),
                "content": message.content,
                "date": message.timestamp
            })
        return Response({
            'messages': sender_messages
        })


class GetRecipientMessageView(generics.GenericAPIView):
    serializer_class = GetRecipientMessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipient_id = request.user.id
        messages = Message.objects.filter(recipient_id=recipient_id).all()
        recipient_messages = []
        for message in messages:
            recipient_messages.append({
                "id": message.id,
                "sender_id": str(message.sender),
                "recipient_id": str(message.recipient),
                "content": message.content,
                "date": message.timestamp
            })
        return Response({
            'messages': recipient_messages
        })


class SendInBasketView(generics.GenericAPIView):
    serializer_class = SendInBasketSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data['list_messages']
        messages_in_basket = []
        for message in messages:
            db_message = Message.objects.get(id=message)
            db_message.send_in_basket_id = request.user.id
            if db_message.send_in_basket_id == request.user.id:
                db_message.in_basket = True
                db_message.save()
                messages_in_basket.append({
                    "sender_id": str(db_message.sender),
                    "recipient_id": str(db_message.recipient),
                    "content": db_message.content,
                    "date": db_message.timestamp,
                    "in_basket": db_message.in_basket
                })
            else:
                return Response({"error": "У вас нет прав на это сообщение."}, status=403)
        return Response({
            'messages': messages_in_basket
        })


class GetBasketView(generics.GenericAPIView):
    serializer_class = GetBasketSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = Message.objects.filter(in_basket=True).all()
        basket_messages = []
        for message in messages:
            if message.send_in_basket_id == request.user.id:
                basket_messages.append({
                    "id": message.id,
                    "sender_id": str(message.sender),
                    "recipient_id": str(message.recipient),
                    "content": message.content,
                    "date": message.timestamp
                })
        return Response({
            'messages': basket_messages
        })