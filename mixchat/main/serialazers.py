import random
from rest_framework import serializers
from .models import ChatUser
from django.core.mail import send_mail


def send_code_to_email(email, user_name, code):
    send_mail(
        f"{user_name}, ваш код подтверждения",
        f"Mixchat, Код подтверждения: {code}. Никому не передавайте этот код!",
        "mixrechecosystem@gmail.com",
        [email]
    )


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = ChatUser
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        email = validated_data["email"]
        validated_data["is_active"] = False
        code = random.randint(1000, 9999)
        validated_data["code"] = code
        user = ChatUser.objects.create_user(**validated_data)
        print('EMAIL', email)
        send_code_to_email(email, user.username, code)
        return user


class SendCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)


class ProfileformSerializer(serializers.Serializer):
    photo = serializers.ImageField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    date_birth = serializers.DateField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True)


class MessageSerializer(serializers.Serializer):
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


class ChatSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField(required=False)
    users = serializers.ListField(max_length=200, required=False, allow_empty=True)
    name = serializers.CharField(max_length=200, required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    type = serializers.CharField(max_length=200, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=200, required=False, allow_blank=True)


class GetChatsSerializer(serializers.Serializer):
    pass


class SendMessageToChatSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    sender_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()
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

