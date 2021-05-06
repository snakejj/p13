from django.urls import path
from videos import views

app_name = "comments"

urlpatterns = [
    path('video-aleatoire', views.random_video, name='random_video')
]
