import os
import requests
from django.contrib import messages
from django.db.models import Q
from comments.models import Comment
from videos.models import Video, AbuseVideo, RateVideo
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def get_report_pending():
    count = AbuseVideo.objects.filter(report_dealt_with=False).count()
    url = "/superadminvideos/abusevideo/?report_dealt_with__exact=0"
    report_pending = {
        'count': count,
        'url': url,

    }
    return report_pending


def get_videos_count():
    count = Video.objects.all().count()
    url = "/superadminvideos/video/"
    all_videos = {
        'count': count,
        'url': url,

    }
    return all_videos


def get_comments_count():
    count = Comment.objects.all().count()
    url = "/superadmincomments/comment/"
    all_comments = {
        'count': count,
        'url': url,

    }
    return all_comments


def get_videos_rated_count():
    count = Video.objects.filter(~Q(average_interest_rating=None)).count()
    url = "/superadminvideos/video/?o=5"
    all_videos_rated = {
        'count': count,
        'url': url,

    }
    return all_videos_rated


def get_rating_count():
    count = RateVideo.objects.all().count()
    url = "/superadminvideos/ratevideo/"
    all_rating = {
        'count': count,
        'url': url,

    }
    return all_rating
