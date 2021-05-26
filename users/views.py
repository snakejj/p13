from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import logout as log_out
from django.contrib.auth import login as log_in
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from comments.managers import CommentManager
from videos.api_random_client import ApiRandomOrg
from videos.forms import LinkForm
from videos.managers import VideoManager, AbuseVideoManager, RateVideoManager


def dashboard(request):
    video = VideoManager()
    abuse = AbuseVideoManager()
    rate = RateVideoManager()
    comment = CommentManager()
    api_instance = ApiRandomOrg()

    nb_requests_used, daily_api_limit = api_instance.get_api_usage(request)
    all_videos = video.get_videos_count()
    all_comments = comment.get_comments_count()
    report_pending = abuse.get_report_pending()
    all_videos_rated = rate.get_videos_rated_count()
    all_ratings = rate.get_rating_count()
    top_5_videos = video.getting_top_videos(request)

    return render(request, 'users/dashboard.html', {
        'title': "Tableau de bord",
        'report_pending': report_pending,
        'nb_requests': nb_requests_used,
        'daily_api_limit': daily_api_limit,
        'all_videos': all_videos,
        'all_comments': all_comments,
        'all_videos_rated': all_videos_rated,
        'all_ratings': all_ratings,
        'top_5_videos': top_5_videos,
    })


def logout(request):
    log_out(request)
    messages.info(request, "On espere vous revoir bientot !", fail_silently=True)
    return redirect("core:home")


def login(request):
    link_form = LinkForm(prefix='video')

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        try:
            user_inst = User.objects.get(username=request.POST.get("username"))
            user_active = user_inst.is_active
            if user_active is False:
                messages.warning(
                    request,
                    "Merci de cliquer sur le lien envoyé dans votre boite mail !",
                    fail_silently=True
                )
                return redirect('users:login')
            else:
                if form.is_valid():
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password')
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        log_in(request, user)
                        messages.info(request, f"Bienvenue {username} !", fail_silently=True)
                        return redirect('users:dashboard')

                else:
                    messages.error(request, "Nom d'utilisateur ou mot de passe incorrect", fail_silently=True)
        except:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect", fail_silently=True)
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {"form": form, 'title': "Connexion", 'link_form': link_form, })
