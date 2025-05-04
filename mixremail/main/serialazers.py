from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # чтобы пароль не возвращался в ответе
        }

    def create(self, validated_data):
        # Хешируем пароль перед сохранением
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # чтобы пароль не возвращался в ответе
        }


class SendMessageSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField()
    content = serializers.CharField(max_length=200)


class GetSendMessageSerializer(serializers.Serializer):
    pass


class GetRecipientMessageSerializer(serializers.Serializer):
    pass


class SendInBasketSerializer(serializers.Serializer):
    list_messages = serializers.ListField()


class GetBasketSerializer(serializers.Serializer):
    pass
