from django.urls import path, include

from . import views

app_name = "users"

urlpatterns = [
    path('connexion/', views.login, name='login'),
    path('admin/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.account_activation, name='activate'),
    path('admin/videos', views.videos_list, name='videos_list'),
    path('admin/comments', views.comments_list, name='comments_list'),
]

