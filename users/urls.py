from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('connexion', views.login, name='login'),
    path('admin', views.dashboard, name='dashboard'),
    path('logout', views.logout, name='logout'),
]
