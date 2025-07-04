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
    content = serializers.CharField(max_length=200, required=False, allow_blank=True)
    chat_id = serializers.IntegerField()
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.FileField(required=False, allow_null=True)
    audio = serializers.FileField(required=False, allow_null=True)

    def validate(self, data):
        # Проверяем, что хотя бы одно из полей content, image, video или audio заполнено
        if not (data.get('content') or data.get('image') or data.get('video') or data.get('audio')):
            raise serializers.ValidationError(
                "Должно быть заполнено хотя бы одно из полей: content, image, video или audio."
            )
        return data


class SearchUserSerializer(serializers.Serializer):
    pass


class GetOneChatSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()


class GetChatsSerializer(serializers.Serializer):
    pass


class CreateChatSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()


class MessageSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()


class SendMessageToChatSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    sender_id = serializers.IntegerField()
    content = serializers.CharField()


class CreateChannelSerializer(serializers.Serializer):
    name = serializers.CharField()


class SubscribeToChannelSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    channel_id = serializers.IntegerField()


class SendMessageToChannelSerializer(serializers.Serializer):
    chanel_id = serializers.IntegerField()
    sender_id = serializers.IntegerField()
    content = serializers.CharField()
