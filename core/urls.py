from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.home, name='home'),
    path('video-aleatoire/', views.random_video, name='random_video'),
    path('mentions-legales/', views.legal_notice, name='legal_notice'),
    path('connexion/', views.login, name='login'),
]
