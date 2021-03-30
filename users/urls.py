from django.urls import path, include

from . import views

app_name = "users"

urlpatterns = [
    path('connexion/', views.login, name='login'),
    path('admin/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('admin/videos', views.videos_list, name='videos_list'),
    path('admin/comments', views.comments_list, name='comments_list'),
    path('admin/moderation-video', views.moderation_video, name='moderation_video'),
]

