from django.urls import path, include

from . import views

app_name = "videos"

urlpatterns = [
    # path('admin/videos', views.videos_list, name='videos_list'),
    # path('admin/moderation-video', views.moderation_video, name='moderation_video'),
    path('video-aleatoire/', views.random_video, name='random_video'),
    path('top-videos/', views.top_videos, name='top_videos'),
]

