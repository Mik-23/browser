from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, LoginSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login = serializer.validated_data['login']
        users = User.objects.all()
        for user in users:
            if user.login == login:
                refresh = RefreshToken.for_user(user)
                user_id = user.id
                current_user = user.login
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user_id,
            'user': current_user
        })