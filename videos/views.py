from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from videos.models import *

# Create your views here.


def videos_list(request):
    return render(request, 'users/videos_list.html', {'title': "Liste des vidéos"})


def moderation_video(request):
    return render(request, 'users/moderation-video.html', {'title': "Modérat° vidéo"})


def random_video(request):
    return render(request, 'videos/random_video.html', {'title': "Vidéo aléatoire", })


def top_videos(request):
    return render(request, 'videos/top_videos.html', {'title': "Top vidéos",})


def submit_video(request):
    if request.POST:
        form = request.POST or None
        link = form.get('link_submitted')

        video = VideoManager()
        clean_link = video.parse_link(request, link)

        if clean_link is False and not request.user.is_authenticated:
            messages.error(
                request,
                "Le lien est incorrect, merci de founir un lien youtube valide",
                fail_silently=True
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            video_is_unique = video.add_video(request, clean_link)
            if video_is_unique is True:
                messages.success(request, "Votre vidéo à bien été ajouté en base de données", fail_silently=True)

                request.session['has_submit_unique_video'] = True

                video = VideoManager()
                request.session['video_link'], api_worked = video.select_random_video()

                if api_worked:
                    return render(request, 'videos/random_video.html', {'title': "Vidéo aléatoire", })

                elif not api_worked:
                    return render(request, 'videos/random_video.html', {'title': "Vidéo (pseudo) aléatoire", })

            elif video_is_unique is False:
                messages.warning(request, "Cette vidéo à deja été proposé, pensez à proposer une autre vidéo",
                                 fail_silently=True)

                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            elif video_is_unique is None:
                messages.error(
                    request,
                    "Le lien est incorrect, merci de founir un lien youtube valide",
                    fail_silently=True
                )

                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return render(request, 'videos/random_video.html', {'title': "Vidéo aléatoire", })
