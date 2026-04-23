from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from .models import ChatUser


class MediaTokenMiddleware:
    """
    Проверяет JWT в cookie только для медиа-запросов
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('media_token')
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                user = ChatUser.objects.filter(id=user_id).first()
                request.user = user
            except (InvalidToken, TokenError):
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        return self.get_response(request)