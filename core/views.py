from django.shortcuts import render

from comments.forms import CommentForm
from videos.forms import LinkForm


def home(request):
    link_form = LinkForm(prefix='video')

    return render(request, 'core/pages/home.html', {
        'title': "Accueil",
        'link_form': link_form, })


def legal_notice(request):
    link_form = LinkForm(prefix='video')

    return render(request, 'core/pages/legal_notice.html', {
        'title': "Mentions légales",
        'link_form': link_form, })


def login(request):
    link_form = LinkForm(prefix='video')

    return render(request, 'core/pages/login.html', {
        'title': "Connexion",
        'link_form': link_form, })

