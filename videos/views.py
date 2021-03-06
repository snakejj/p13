from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from comments.forms import CommentForm, CaptchaForm
from videos.api_random_client import ApiRandomOrg
from videos.forms import LinkForm, ReportForm, RatingForm
from videos.managers import VideoManager, AbuseVideoManager, RateVideoManager
from comments.managers import CommentManager
from comments.models import *
from captcha.image import ImageCaptcha


def top_videos(request):
    video = VideoManager()
    abuse = AbuseVideoManager()
    comment = CommentManager()

    link_form = LinkForm(prefix='video')
    report_form = ReportForm(prefix='report')
    comment_form = CommentForm(prefix='comment')
    captcha_form = CaptchaForm()

    forcing_new_captcha = False

    comment.get_captcha_int(request, forcing_new_captcha)

    captcha_image = ImageCaptcha(width=100, height=52)
    captcha_image.write(str(comment.decrypt(request.session['temp_var'])), 'core/static/img/captcha.png')

    top_5_videos = video.getting_top_videos(request)
    try:
        if request.session['has_submit_report']:
            pass
    except KeyError:
        request.session['has_submit_report'] = []
    try:
        if request.session['has_submit_vote']:
            pass
    except KeyError:
        request.session['has_submit_vote'] = []
    try:
        if request.session['top_video']:
            pass
    except KeyError:
        if len(top_5_videos) > 0:
            request.session['top_video'] = top_5_videos[0].get("video_link")
            video_instance = Video.objects.get(link=request.session['top_video'])
            request.session['top_video_pk'] = video_instance.pk
        else:
            pass
    # This part retrieve the video_url from the top_videos links
    if request.method == 'GET':
        if 'video_link' in request.GET:
            request.session['top_video'] = request.GET.get("video_link")
            video_instance = Video.objects.filter(link=request.session['top_video'])
            try:
                request.session['top_video_pk'] = video_instance[0].pk
            except IndexError:
                messages.error(
                        request, "Le video n'existe pas ou plus", fail_silently=True
                    )

            # try:
            #     request.session['top_video'] = request.GET.get("video_link")
            # except videos.models.Video.DoesNotExist:
            #     messages.error(
            #         request, "Le video n'existe plus", fail_silently=True
            #     )

    if request.method == 'POST':

        if "report_sent" in request.POST:
            report_form = ReportForm(request.POST or None, prefix='report')
            abuse.submit_report_video(request, report_form)
            return redirect("videos:top_videos")

        elif 'comment_sent' in request.POST:
            comment_form = CommentForm(request.POST or None, prefix='comment')

            captcha_input = comment_form.data.get('captcha')

            # We check if the input value is the same as the temp var once decrypted
            if str(captcha_input) == str(comment.decrypt(request.session['temp_var'])):
                comment_submitted = comment.submit_comment(request, comment_form)
                if comment_submitted is True:
                    forcing_new_captcha = True
                    comment.get_captcha_int(request, forcing_new_captcha)
                    return redirect("videos:top_videos")
            else:
                messages.error(
                    request, "Le captcha est incorrect", fail_silently=True
                )

    active_style = "background-color: #cfc3d5; color: black;"

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

    return render(request, 'videos/top_videos.html', {
        'title': "Top vid??os",
        'link_form': link_form,
        'top_5_videos': top_5_videos,
        'active_style': active_style,
        'comments': comments,
        'numb_comments': numb_comments,
        'comment_form': comment_form,
        'report_form': report_form,
        'social_links': social_links,
        'captcha_form': captcha_form,
    })


def random_video(request):
    video = VideoManager()
    rate = RateVideoManager()
    abuse = AbuseVideoManager()
    comment = CommentManager()
    api_instance = ApiRandomOrg()

    link_form = LinkForm(prefix='video')
    report_form = ReportForm(prefix='report')
    rate_form = RatingForm(prefix='rate')
    comment_form = CommentForm(prefix='comment')
    captcha_form = CaptchaForm()

    forcing_new_captcha = False

    comment.get_captcha_int(request, forcing_new_captcha)

    captcha_image = ImageCaptcha(width=100, height=52)
    captcha_image.write(str(comment.decrypt(request.session['temp_var'])), 'core/static/img/captcha.png')

    try:
        if request.session['has_submit_report']:
            pass
    except KeyError:
        request.session['has_submit_report'] = []
    try:
        if request.session['has_submit_vote']:
            pass
    except KeyError:
        request.session['has_submit_vote'] = []

    if request.method == 'GET':
        if 'video_link' in request.GET:
            request.session['video_link'] = request.GET.get("video_link")
            video_instance = Video.objects.filter(~Q(status="OF"), link=request.session['video_link'])
            try:
                request.session['video_pk'] = video_instance[0].pk
                request.session['has_shared_link'] = True
            except IndexError:
                messages.error(
                        request, "Le video n'existe pas ou plus", fail_silently=True
                    )
                return redirect("core:home")

    elif request.method == 'POST':
        if 'link_sent' in request.POST:
            link_form = LinkForm(request.POST or None, prefix='video')

            video_is_unique = video.submit_video(request, link_form)
            if video_is_unique is True:
                request.session['video_pk'], request.session['video_link'] = api_instance.select_random_video(request)

            return redirect("videos:random_video")

        elif 'comment_sent' in request.POST:
            comment_form = CommentForm(request.POST or None, prefix='comment')

            captcha_input = comment_form.data.get('captcha')

            # We check if the input value is the same as the temp var once decrypted
            if str(captcha_input) == str(comment.decrypt(request.session['temp_var'])):
                comment_submitted = comment.submit_comment(request, comment_form)
                if comment_submitted is True:
                    forcing_new_captcha = True
                    comment.get_captcha_int(request, forcing_new_captcha)
                    return redirect("videos:random_video")
            else:
                messages.error(
                    request, "Le captcha est incorrect", fail_silently=True
                )

        elif "report_sent" in request.POST:
            report_form = ReportForm(request.POST or None, prefix='report')
            abuse.submit_report_video(request, report_form)
            return redirect("videos:random_video")

        elif "rating_sent" in request.POST:
            rate_form = RatingForm(request.POST or None, prefix='rate')
            video_rated = rate.submit_rating_video(request, rate_form)
            if video_rated is True:
                request.session['video_pk'], request.session['video_link'] = api_instance.select_random_video(request)

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
                'title': "Vid??o al??atoire",
                'comments': comments,
                'numb_comments': numb_comments,
                'comment_form': comment_form,
                'link_form': link_form,
                'report_form': report_form,
                'rate_form': rate_form,
                'social_links': social_links,
                'captcha_form': captcha_form,
    })
