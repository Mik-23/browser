from django.urls import path
from . import views


urlpatterns = [
    path('', views.site, name='home'),
    path('robots.txt', views.text_view, name='robots')
]
