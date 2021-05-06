from django.urls import path, include

from . import views

app_name = "users"

urlpatterns = [
    path('connexion', views.login, name='login'),
    path('admin', views.dashboard, name='dashboard'),
    path('logout', views.logout, name='logout'),
    # path('admin/comments', views.comments_list, name='comments_list'),
    # path('admin/moderation-commentaires', views.moderation_comment, name='moderation_comment'),
]

