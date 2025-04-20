from django.urls import path
from . import views, api

urlpatterns = [
    path('', views.site, name='home'),
    path('account', views.account, name='account'),
    path('api/register/', api.RegisterView.as_view() , name='register'),
    path('api/login/', api.LoginView.as_view() , name='login')
]
