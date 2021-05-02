import os

import requests
from django.contrib import messages
from django.db import models

from comments.models import Comment
from videos.models import Video, AbuseVideo


def get_report_pending():
    count = AbuseVideo.objects.filter(report_dealt_with=False).count()
    url = "/superadmin/videos/abusevideo/?report_dealt_with__exact=0"
    report_pending = {
        'count': count,
        'url': url,

    }
    return report_pending

def get_api_usage(request):
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json'
    }

    url = "https://api.random.org/json-rpc/4/invoke"

    data = {
        "jsonrpc": "2.0",
        "method": "getUsage",
        "params": {
            "apiKey": os.getenv("RANDOM_API_KEY")
        },
        "id": 15998
    }

    try:
        response = requests.post(url, json=data, headers=headers)
    except requests.exceptions.ConnectionError:
        response = None
    if response is None or response.status_code != 200:
        # If there is an error with the API answer, we assign None to request_left

        messages.info(
            request,
            "L'API de randomisation etant indisponible, il est impossible d'avoir le nombre de requetes restante",
            fail_silently=True
        )
        requests_left = None
    else:
        # If the API answer, we assign the API result to requests_left
        requests_left = response.json()["result"]["requestsLeft"]
        api_monthly_limit = 1000
        nb_requests_used = api_monthly_limit - requests_left

    return nb_requests_used


def get_videos_count():
    count = Video.objects.all().count()
    url = "/superadmin/videos/video/"
    all_videos = {
        'count': count,
        'url': url,

    }
    return all_videos


def get_comments_count():
    count = Comment.objects.all().count()
    url = "/superadmin/comments/comment/"
    all_comments = {
        'count': count,
        'url': url,

    }
    return all_comments


