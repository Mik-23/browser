from django.urls import path
from . import views, api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


urlpatterns = [
    path('chat', views.chat, name='home'),
    path('auth_in_chat', views.auth_in_chat, name='auth_in_chat'),
    path('api/register/', api.RegisterView.as_view(), name='register'),
    path('api/send_message/', api.SendMessageView.as_view(), name='send_message'),
    path('api/search_user/', api.SearchUserView.as_view(), name='search_user'),
    path('api/get_one_chat/', api.GetOneChatView.as_view(), name='get_one_chat'),
    path('api/get_chats/', api.GetChatsView.as_view(), name='get_chats'),
    path('api/create_chat/', api.GreateChatView.as_view(), name='create_chat'),
    path('api/get_messages/', api.MessageView.as_view(), name='get_messages'),
    path('api/create_channel/', api.GreateChannelView.as_view(), name='create_channel'),
    path('api/subscribe_to_channel/', api.SubscribeToChannelView.as_view(), name='subscribe_to_channel'),
    path('api/send_message_to_channel/', api.SendMessageToChannelView.as_view(), name='send_message_to_channel'),
    path('api/login/', api.LoginView.as_view(), name='login'),
    ]