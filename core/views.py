from django.shortcuts import render


def home(request):
    return render(request, 'core/pages/home.html', {'title': "Accueil",})


def legal_notice(request):
    return render(request, 'core/pages/legal_notice.html', {'title': "Mentions légales",})
