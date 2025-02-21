from django.urls import path
from .views import search_view, image_view, video_view

urlpatterns = [
    path('', search_view, name='search'),
    path('image', image_view, name='images'),
    path('video', video_view, name='videos')
]