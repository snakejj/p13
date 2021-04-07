from django.urls import path, include

from . import views

app_name = "videos"

urlpatterns = [
    path('admin/videos', views.videos_list, name='videos_list'),
    path('admin/moderation-video', views.moderation_video, name='moderation_video'),
]

