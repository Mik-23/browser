from django.urls import path
from . import views, api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


urlpatterns = [
    path('mail', views.mail, name='home'),
    path('account', views.account, name='account'),
    path('api/register/', api.RegisterView.as_view(), name='register'),
    path('api/send_message/', api.SendMessageView.as_view(), name='send_message'),
    path('api/get_send_message/', api.GetSendMessageView.as_view(), name='get_send_message'),
    path('api/get_recipient_message/', api.GetRecipientMessageView.as_view(), name='get_recipient_message'),
    path('api/send_in_basket/', api.SendInBasketView.as_view(), name='send_in_basket'),
    path('api/get_basket/', api.GetBasketView.as_view(), name='get_basket'),
    path('api/login/', api.LoginView.as_view(), name='login'),
    ]