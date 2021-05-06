from django.urls import path

from . import views

app_name = "videos"

urlpatterns = [
    path('video-aleatoire', views.random_video, name='random_video'),
    path('top-videos', views.top_videos, name='top_videos'),
]
