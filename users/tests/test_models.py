import pytest

import requests
from django.contrib.sessions.middleware import SessionMiddleware
from requests.exceptions import ConnectionError
import responses

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from mixer.backend.django import mixer

from users.models import get_report_pending, get_api_usage, get_videos_count, get_comments_count, \
    get_videos_rated_count, get_rating_count
from videos.forms import LinkForm
from videos.models import VideoManager

pytestmark = pytest.mark.django_db


def test_get_report_pending():

    mixer.blend('videos.AbuseVideo', report_dealt_with=False)
    mixer.blend('videos.AbuseVideo', report_dealt_with=False)
    mixer.blend('videos.AbuseVideo', report_dealt_with=True)
    mixer.blend('videos.AbuseVideo', report_dealt_with=False)
    mixer.blend('videos.AbuseVideo', report_dealt_with=True)
    mixer.blend('videos.AbuseVideo', report_dealt_with=False)

    report_pending = get_report_pending()
    assert report_pending['count'] == 4
    assert report_pending['url'] == "/superadmin/videos/abusevideo/?report_dealt_with__exact=0"


@responses.activate
def test_get_api_usage_expected():
    # Scenario where the API answer with a status code 200
    responses.add(
        responses.POST,
        'https://api.random.org/json-rpc/4/invoke',
        json={
            "jsonrpc": "2.0",
            "result": {
                "status": "running",
                "creationTime": "2013-02-01 17:53:40Z",
                "bitsLeft": 998532,
                "requestsLeft": 458,
                "totalBits": 1646421,
                "totalRequests": 65036
            },
            "id": 15998
        },
        status=200
    )
    requests.post('https://api.random.org/json-rpc/4/invoke')

    req = RequestFactory().get('/admin/')
    req.user = AnonymousUser()

    nb_requests_used = get_api_usage(req)

    assert nb_requests_used == 1000 - 458, \
        'Should return the value of the api_monthly_limit (1000) minus the "requestsLeft" (458), so 1000-458= 542 '


@responses.activate
@pytest.mark.xfail(raises=ConnectionError)
def test_get_api_usage_when_api_does_not_answer_or_not_as_expected():

    request = RequestFactory().get('/admin/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    nb_requests_used = get_api_usage(request)

    assert nb_requests_used is None


def test_get_videos_count():
    mixer.blend('videos.Video')
    mixer.blend('videos.Video')
    mixer.blend('videos.Video')
    mixer.blend('videos.Video')
    mixer.blend('videos.Video')

    all_videos = get_videos_count()

    assert all_videos['count'] == 5
    assert all_videos['url'] == "/superadmin/videos/video/"


def test_get_comments_count():
    mixer.blend('comments.Comment')
    mixer.blend('comments.Comment')

    all_comments = get_comments_count()

    assert all_comments['count'] == 2
    assert all_comments['url'] == "/superadmin/comments/comment/"


def test_get_videos_rated_count():
    mixer.blend('videos.Video', average_interest_rating=None)
    mixer.blend('videos.Video', average_interest_rating=7.8)
    mixer.blend('videos.Video', average_interest_rating=3.5)
    mixer.blend('videos.Video', average_interest_rating=8.2)
    mixer.blend('videos.Video', average_interest_rating=9)
    mixer.blend('videos.Video', average_interest_rating=7)
    mixer.blend('videos.Video', average_interest_rating=None)
    mixer.blend('videos.Video', average_interest_rating=8.2)

    all_videos_rated = get_videos_rated_count()

    assert all_videos_rated['count'] == 6
    assert all_videos_rated['url'] == "/superadmin/videos/video/?o=5"


def test_get_rating_count():
    mixer.blend('videos.RateVideo')
    mixer.blend('videos.RateVideo')
    mixer.blend('videos.RateVideo')
    mixer.blend('videos.RateVideo')
    mixer.blend('videos.RateVideo')

    all_rating = get_rating_count()

    assert all_rating['count'] == 5
    assert all_rating['url'] == "/superadmin/videos/ratevideo/"
