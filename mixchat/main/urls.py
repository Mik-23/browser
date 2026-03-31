from django.urls import path
from . import views, api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


urlpatterns = [
    path('', views.chat, name='chat_url'),
    path('auth_in_chat', views.auth_in_chat, name='auth_in_chat'),
    path('register_in_chat', views.register_in_chat, name='register_in_chat'),
    path('successfully', views.successfully, name='successfully'),
    path('confirmation_code', views.confirmation_code, name='confirmation_code'),
    path('privacy_policy', views.privacy_policy, name='privacy_policy'),
    path('agreement', views.agreement, name='agreement'),
    path('profile_current_user', views.profile_current_user, name='profile_current_user'),
    path('profile_other_user/<str:username>', views.profile_other_user, name='profile_other_user'),
    path('create_group', views.create_group, name='create_group'),
    path('edit_group/<str:name>', views.edit_group, name='edit_group'),
    path('api/reg/', api.RegisterView.as_view(), name='reg'),
    path('api/send_code/', api.SendCodeView.as_view(), name='send_code'),
    path('api/resend_code/', api.ResendCodeView.as_view(), name='resend_code'),
    path('api/profile_form/', api.ProfileformView.as_view(), name='profile_form'),
    path('api/message/', api.MessageView.as_view(), name='message'),
    path('api/message/count/', api.MessageCountView.as_view(), name='message_count'),
    path('api/save_fcm/', api.SaveFCMToken.as_view(), name='save_fcm'),
    path('api/search_user/', api.SearchUserView.as_view(), name='search_user'),
    path('api/current_user/', api.GetCurrentUserView.as_view(), name='current_user'),
    path('api/chat/', api.ChatView.as_view(), name='chat'),
    path('api/delete_user_from_group/', api.DeleteUserFromGroup.as_view(), name='delete_user_from_group'),
    path('api/get_chats/', api.GetChatsView.as_view(), name='get_chats'),
    path('api/create_channel/', api.GreateChannelView.as_view(), name='create_channel'),
    path('api/subscribe_to_channel/', api.SubscribeToChannelView.as_view(), name='subscribe_to_channel'),
    path('api/send_message_to_channel/', api.SendMessageToChannelView.as_view(), name='send_message_to_channel'),
    path('api/login/', api.LoginView.as_view(), name='login'),
    path('api/logout/', api.LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]
