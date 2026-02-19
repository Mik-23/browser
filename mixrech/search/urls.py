from django.urls import path
from .views import search_view, image_view, video_view, search_by_image_view, news_view
from .api import VoiceView

urlpatterns = [
    path('', search_view, name='search'),
    path('image', image_view, name='images'),
    path('video', video_view, name='videos'),
    path('search_by_image', search_by_image_view, name='search_by_image'),
    path('news', news_view, name='news'),
    path('api/voice', VoiceView.as_view(), name='voice')
]
