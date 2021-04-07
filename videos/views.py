from django.shortcuts import render
from django.contrib import messages

# Create your views here.


def videos_list(request):
    return render(request, 'users/videos_list.html', {'title': "Liste des vidéos"})


def moderation_video(request):
    return render(request, 'users/moderation-video.html', {'title': "Modérat° vidéo"})
