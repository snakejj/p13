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
        response = requests.post(url, json=data, headers=headers, timeout=5)

    except (requests.exceptions.ConnectionError, requests.Timeout):
        response = None

    api_daily_limit = int(os.getenv("API_DAILY_LIMIT"))

    if response is None or response.status_code != 200:
        # If there is an error with the API answer, we assign None to request_left

        messages.info(
            request,
            "L'API de randomisation etant indisponible, il est impossible d'avoir le nombre de requetes restante",
            fail_silently=True
        )
        nb_requests_used = None
    else:
        # If the API answer, we assign the API result to requests_left
        requests_left = response.json()["result"]["requestsLeft"]
        nb_requests_used = api_daily_limit - requests_left

    return nb_requests_used, api_daily_limit


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
