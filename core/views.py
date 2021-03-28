from django.shortcuts import render


def home(request):
    return render(request, 'core/pages/home.html', {'title': "Accueil",})


def legal_notice(request):
    return render(request, 'core/pages/legal_notice.html', {'title': "Mentions légales",})


def login(request):
    return render(request, 'core/pages/login.html', {'title': "Connexion",})

def random_video(request):
    return render(request, 'core/pages/random_video.html', {'title': "Vidéo aléatoire",})