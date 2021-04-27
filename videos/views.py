from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from comments.forms import CommentForm
from videos.forms import LinkForm, ReportForm

from videos.models import *
from comments.models import *


# Create your views here.


def videos_list(request):
    return render(request, 'users/videos_list.html', {'title': "Liste des vidéos"})


def moderation_video(request):
    return render(request, 'users/moderation-video.html', {'title': "Modérat° vidéo"})


def top_videos(request):
    link_form = LinkForm(prefix='video')

    return render(request, 'videos/top_videos.html', {
        'title': "Top vidéos",
        'link_form': link_form, })


def random_video(request):
    video = VideoManager()
    comment = CommentManager()

    comment_form = CommentForm(prefix='comment')
    link_form = LinkForm(prefix='video')
    report_form = ReportForm(prefix='report')

    if request.method == 'GET':
        if 'video_link' in request.GET:
            request.session['video_link'] = request.GET.get("video_link")
            try:
                video_shared = Video.objects.get(link=request.session['video_link'])
                request.session['video_pk'] = video_shared.pk
                request.session['has_submit_unique_video'] = True
            except videos.models.Video.DoesNotExist:
                messages.error(
                    request, "Le video n'existe pas ou plus", fail_silently=True
                )
                return redirect("core:home")

    elif request.method == 'POST':
        if 'link_sent' in request.POST:
            link_form = LinkForm(request.POST or None, prefix='video')

            video_is_unique = video.submit_video(request, link_form)
            if video_is_unique is True:
                request.session['video_pk'], request.session['video_link'] = video.select_random_video(request)
                request.session['has_submit_report'] = False

            return redirect("videos:random_video")

        elif 'comment_sent' in request.POST:
            comment_form = CommentForm(request.POST or None, prefix='comment')
            comment_submitted = comment.submit_comment(request, comment_form)
            if comment_submitted is True:
                return redirect("videos:random_video")

        elif "report_sent" in request.POST:
            report_form = ReportForm(request.POST or None, prefix='report')
            video.submit_report_video(request, report_form)
            return redirect("videos:random_video")

    try:
        comments = comment.list_comments(request)
        numb_comments = len(comments)
    except TypeError:
        comments = None
        numb_comments = 0

    try:
        social_links = video.generate_share_link(request, request.session['video_link'])
    except KeyError:
        social_links = None

    return render(request, 'videos/random_video.html', {
                'title': "Vidéo aléatoire",
                'comments': comments,
                'numb_comments': numb_comments,
                'comment_form': comment_form,
                'link_form': link_form,
                'report_form': report_form,
                'social_links': social_links, })


