import pytest

import requests
from django.contrib.sessions.middleware import SessionMiddleware
from requests.exceptions import ConnectionError
import responses

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from mixer.backend.django import mixer

from videos.forms import LinkForm
from videos.models import VideoManager

pytestmark = pytest.mark.django_db


class TestVideoManager:
    def test__parse_link(self):
        admin = mixer.blend('auth.User', id=1)
        req = RequestFactory().get('/')
        req.user = admin

        req2 = RequestFactory().get('/')
        req2.user = AnonymousUser()

        raw_url_1 = "http://youtu.be/6avJHaC3C2U"
        raw_url_2 = "http://www.youtube.com/watch?v=6avJHaC3C2U&feature=feedu"
        raw_url_3 = "http://www.youtube.com/embed/6avJHaC3C2U"
        raw_url_4 = "http://www.youtube.com/v/6avJHaC3C2U?version=3&amp;hl=en_US"
        raw_wrong_url_as_admin = "dsqoiudsqoiujdsq"
        raw_wrong_url_as_anonymous_user = "dsqoiudsqoiujdsq"

        video = VideoManager()
        clean_url_1 = video._parse_link(req, raw_url_1)
        clean_url_2 = video._parse_link(req, raw_url_2)
        clean_url_3 = video._parse_link(req, raw_url_3)
        clean_url_4 = video._parse_link(req, raw_url_4)
        clean_wrong_url_as_admin = video._parse_link(req, raw_wrong_url_as_admin)
        clean_wrong_url_as_guest = video._parse_link(req2, raw_wrong_url_as_anonymous_user)

        assert len(clean_url_1) == 11, 'The clean url should be 11 character long'
        assert clean_url_1 == "6avJHaC3C2U", 'The clean url should be "6avJHaC3C2U"'
        assert len(clean_url_2) == 11, 'The clean url should be 11 character long'
        assert clean_url_2 == "6avJHaC3C2U", 'The clean url should be "6avJHaC3C2U"'
        assert len(clean_url_3) == 11, 'The clean url should be 11 character long'
        assert clean_url_3 == "6avJHaC3C2U", 'The clean url should be "6avJHaC3C2U"'
        assert len(clean_url_4) == 11, 'The clean url should be 11 character long'
        assert clean_url_4 == "6avJHaC3C2U", 'The clean url should be "6avJHaC3C2U"'

        assert clean_wrong_url_as_admin is True, 'Should return True if url is wrong but user is connected (as admin)'
        assert clean_wrong_url_as_guest is False, 'Should return False if url is wrong and user is not connected'

    def test__add_videdo(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We make a video so that we check the behavior when a videdo already exists
        clean_link = "6avJHaC3C2U"
        mixer.blend('videos.Video', link=clean_link)
        # ##########################################################################
        video = VideoManager()

        video_already_exist = video._add_video(req, clean_link)
        new_video = video._add_video(req, "uvf0lD5xzH0")

        assert video_already_exist is False, 'Should return False when video already exists'
        assert new_video is True, 'Should return True when video does not exists in database'

    @responses.activate
    def test_select_random_video_expected(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We populate the DB in order for the function to be able to randomly select an item from
        mixer.blend('videos.Video', pk=3548, link="VPkbtMLGtoc", status="IN")    # Entry N°0 in the db
        mixer.blend('videos.Video', pk=6846, link="rUOnbRFmWao", status="IN")    # Entry N°1 in the db
        mixer.blend('videos.Video', pk=8813, link="ZUQubYqVZyn", status="IN")    # Entry N°2 in the db
        mixer.blend('videos.Video', pk=9102, link="krfeBAJCTQh", status="IN")    # Entry N°3 in the db
        mixer.blend('videos.Video', pk=9358, link="VjEKKrevKva", status="IN")    # Entry N°4 in the db
        mixer.blend('videos.Video', pk=9998, link="djOLmtIIDsn", status="IN")    # Entry N°5 in the db


        # Scenario where the API answer with a status code 200
        responses.add(
            responses.POST,
            'https://api.random.org/json-rpc/4/invoke',
            json={
                "jsonrpc": "2.0",
                "result": {
                    "random": {
                        "data": [
                            3
                        ],
                        "completionTime": "2011-10-10 13:19:12Z"
                    },
                    "bitsUsed": 16,
                    "bitsLeft": 199984,
                    "requestsLeft": 9999,
                    "advisoryDelay": 0
                },
                "id": 42,
            },
            status=200
        )

        requests.post('https://api.random.org/json-rpc/4/invoke')

        video = VideoManager()
        test = video.select_random_video(req)

        assert test == (9102, "krfeBAJCTQh"), 'Should return the pk and link of the 3rd entry in DB (at index 0)'

    @responses.activate
    def test_select_random_video_status_not_200(self, monkeypatch):
        # ##############################################################################################################
        # Scenario where the API returns a status code != than 200
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We populate the DB in order for the function to be able to randomly select an item from
        mixer.blend('videos.Video', pk=3548, link="VPkbtMLGtoc", status="IN")  # Entry N°0 in the db
        mixer.blend('videos.Video', pk=6846, link="rUOnbRFmWao", status="IN")  # Entry N°1 in the db
        mixer.blend('videos.Video', pk=8813, link="ZUQubYqVZyn", status="IN")  # Entry N°2 in the db
        mixer.blend('videos.Video', pk=9102, link="krfeBAJCTQh", status="IN")  # Entry N°3 in the db
        mixer.blend('videos.Video', pk=9358, link="VjEKKrevKva", status="IN")  # Entry N°4 in the db
        mixer.blend('videos.Video', pk=9998, link="djOLmtIIDsn", status="IN")  # Entry N°5 in the db

        responses.add(
            responses.POST,
            'https://api.random.org/json-rpc/4/invoke',
            json={},
            status=300
        )

        requests.post('https://api.random.org/json-rpc/4/invoke')

        # We simulate the randrange output and choose the 4th entry in db
        monkeypatch.setattr('videos.models.randrange', lambda a, b: 4)

        video = VideoManager()
        test = video.select_random_video(req)

        assert test == (9358, "VjEKKrevKva"), 'Should return the pk and link of the 4th entry in DB (at index 0)'

        # ##############################################################################################################

    @responses.activate
    @pytest.mark.xfail(raises=KeyError)
    def test_select_random_video_when_only_one_video_in_db(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We populate the DB in order for the function to be able to randomly select an item from
        mixer.blend('videos.Video', pk=3548, link="VPkbtMLGtoc", status="IN")  # Entry N°0 in the db

        # Scenario where the API answer with a status code 200
        responses.add(
            responses.POST,
            'https://api.random.org/json-rpc/4/invoke',
            json={
                'jsonrpc': '2.0',
                'error': {
                    'code': 300,
                    'message': "Parameter 'min' must be less than parameter 'max'",
                    'data': ['min', 'max']},
                'id': 42
            },
            status=200
        )

        requests.post('https://api.random.org/json-rpc/4/invoke')

        video = VideoManager()
        test = video.select_random_video(req)

        assert test == (3548, "VPkbtMLGtoc"), 'Should return the pk and link of the 3rd entry in DB (at index 0)'

    @responses.activate
    @pytest.mark.xfail(raises=ConnectionError)
    def test_select_random_video_connexion_error(self, monkeypatch):
        # ##############################################################################################################
        # Scenario where there is a connection error while reaching the API
        # We populate the DB in order for the function to be able to randomly select an item from
        mixer.blend('videos.Video', pk=3548, link="VPkbtMLGtoc", status="IN")  # Entry N°0 in the db
        mixer.blend('videos.Video', pk=6846, link="rUOnbRFmWao", status="IN")  # Entry N°1 in the db
        mixer.blend('videos.Video', pk=8813, link="ZUQubYqVZyn", status="IN")  # Entry N°2 in the db
        mixer.blend('videos.Video', pk=9102, link="krfeBAJCTQh", status="IN")  # Entry N°3 in the db
        mixer.blend('videos.Video', pk=9358, link="VjEKKrevKva", status="IN")  # Entry N°4 in the db
        mixer.blend('videos.Video', pk=9998, link="djOLmtIIDsn", status="IN")  # Entry N°5 in the db
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We simulate the randrange output and choose the 4th entry in db
        monkeypatch.setattr('videos.models.randrange', lambda a, b: 4)

        video = VideoManager()

        assert video.select_random_video(req) == (9358, 'VjEKKrevKva')

    def test_submit_video(self):
        # ##############################################################################################################
        # Scenario where the link submitted is valid and unique

        request = RequestFactory().get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        link_form = LinkForm(data={
            'video-link': "http://youtu.be/SA2iWivDJiE",
        })

        video = VideoManager()
        return_of_the_function = video.submit_video(request, link_form)

        assert return_of_the_function is True
        assert request.session['has_submit_unique_video'] is True

        # ##############################################################################################################
        # Scenario where the link submitted is valid and not unique

        # We populate the DB in order for the function to detect that the link submitted exists already
        mixer.blend('videos.Video', pk=4821, link="VPkbtMLzeoc", status="IN")  # Entry N°0 in the db

        link_form_url_already_exists = LinkForm(data={
            'video-link': "http://youtu.be/VPkbtMLzeoc",
        })

        video = VideoManager()
        return_of_the_function = video.submit_video(request, link_form)

        assert return_of_the_function is False

        # ##############################################################################################################
        # Scenario where the link, valid or not, is submitted by the admin

        admin = mixer.blend('auth.User', id=1)
        request.user = admin

        link_form_url_submitted_by_admin = LinkForm(data={
            'video-link': "bla bla bla",
        })

        video = VideoManager()
        return_of_the_function = video.submit_video(request, link_form_url_submitted_by_admin)

        assert return_of_the_function is True
        assert request.session['has_submit_unique_video'] is True

        # ##############################################################################################################
        # Scenario where the link submitted is not valid and not connected

        request.user = AnonymousUser()

        link_form_url_invalid = LinkForm(data={
            'vk': 1.3333,
        })

        video = VideoManager()
        return_of_the_function = video.submit_video(request, link_form_url_invalid)

        assert return_of_the_function is None

    def test_submit_report_video(self):
        # ##############################################################################################################
        # Scenario where the video is in status != from "ON" on page /video-aleatoire

        # We populate the DB
        mixer.blend('videos.Video', pk=4821, link="VPkbtMLzeoc", status="IN")  # Entry N°0 in the db

        request = RequestFactory().get('/video-aleatoire/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_report'] = []
        request.session['video_link'] = "VPkbtMLzeoc"
        request.session.save()

        report_form = LinkForm(
            data={
                'report-reason': "V",
                'report-message': "Random message",
                'video': "4821",
            }
        )

        video = VideoManager()
        video.submit_report_video(request, report_form)

        assert "VPkbtMLzeoc" in request.session['has_submit_report']

        # ##############################################################################################################
        # Scenario where the video is in status "ON" on page /video-aleatoire

        # We populate the DB
        mixer.blend('videos.Video', pk=4821, link="VBkbtMLze1c", status="ON")  # Entry N°0 in the db

        request = RequestFactory().get('/video-aleatoire/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_report'] = []
        request.session['video_link'] = "VBkbtMLze1c"
        request.session.save()

        report_form = LinkForm(
            data={
                'report-reason': "V",
                'report-message': "Random message",
                'video': "4821",
            }
        )

        video = VideoManager()
        video.submit_report_video(request, report_form)

        assert "VBkbtMLze1c" in request.session['has_submit_report']

        # ##############################################################################################################
        # Scenario where the video is in status != from "ON" on page /top-videos

        # We populate the DB
        mixer.blend('videos.Video', pk=4821, link="VPkbtMLze0c", status="IN")  # Entry N°0 in the db

        request = RequestFactory().get('/top-videos/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_report'] = []
        request.session['top_video'] = "VPkbtMLze0c"
        request.session.save()

        report_form = LinkForm(
            data={
                'report-reason': "V",
                'report-message': "Random message",
                'video': "4821",
            }
        )

        video = VideoManager()
        video.submit_report_video(request, report_form)

        assert "VPkbtMLze0c" in request.session['has_submit_report']

        # ##############################################################################################################
        # Scenario where the video is in status "ON" on page /top-videos

        # We populate the DB
        mixer.blend('videos.Video', pk=4821, link="VPkbtMLze1c", status="ON")  # Entry N°0 in the db

        request = RequestFactory().get('/top-videos/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_report'] = []
        request.session['top_video'] = "VPkbtMLze1c"
        request.session.save()

        report_form = LinkForm(
            data={
                'report-reason': "V",
                'report-message': "Random message",
                'video': "4821",
            }
        )

        video = VideoManager()
        video.submit_report_video(request, report_form)

        assert "VPkbtMLze1c" in request.session['has_submit_report']

    def test_generate_share_link_when_everything_is_ok(self):
        request = RequestFactory().get('/top-video')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['top_video'] = "VPkbtMLzeoc"
        request.session.save()

        video_link = "VPkbtMLzeoc"

        video = VideoManager()
        return_of_the_function = video.generate_share_link(request, video_link)

        assert "http://www.linkedin.com/shareArticle?mini=true&url=http://testserver/video-aleatoire/?video_link=VPkbtMLzeoc" \
               in return_of_the_function

    @pytest.mark.xfail(raises=TypeError)
    def test_generate_share_link_with_except_handling(self):
        request = RequestFactory().get('/top-video')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['top_video'] = 1
        request.session.save()

        video_link = "VPkbtMLzeoc"

        video = VideoManager()
        return_of_the_function = video.generate_share_link(request, video_link)

        assert return_of_the_function == {}

    @pytest.mark.xfail(raises=KeyError)
    def test_submit_rating_video(self):

        # ##############################################################################################################
        # Scenario where ratings does not exists yet

        # We populate the DB in order for the function to detect that the link submitted exists already
        mixer.blend('videos.Video', pk=4821, link="VPkbtMLzeoc", status="IN")  # Entry N°0 in the db

        request = RequestFactory().get('/video-aleatoire')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['video_link'] = "VPkbtMLzeoc"
        request.session.save()

        rating_form = LinkForm(data={
            'rate-interest': 1,
            'rate-quality': 5,
            'video': "4821",
        })

        video = VideoManager()
        return_of_the_function = video.submit_rating_video(request, rating_form)

        assert return_of_the_function is True

        # ##############################################################################################################
        # Scenario where ratings already exists

        # We populate the DB
        video_instance = mixer.blend('videos.Video', pk=4821, link="VPkbtMLzeoc", status="IN")  # Entry N°0 in the db
        mixer.blend("videos.RateVideo", video=video_instance, interest_rating=5, quality_rating=4)

        request = RequestFactory().get('/video-aleatoire/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        rating_form = LinkForm(data={
            'rate-interest': 1,
            'rate-quality': 5,
            'video': "4821",
        })

        video = VideoManager()
        return_of_the_function = video.submit_rating_video(request, rating_form)

        assert return_of_the_function is True

    def test_getting_top_videos_with_at_least_5_rated_videos(self):
        # ##############################################################################################################
        # Scenario where the DB is populated with at least 5 videos rated
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We populate the DB in order for the function to be able to randomly select an item from
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=2, status="OF", link="2QwgLSVtYvG", average_interest_rating=6,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=3, status="IN", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=4, status="IN", link="4QwgLSVtYvG", average_interest_rating=3,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=5, status="IN", link="5QwgLSVtYvG", average_interest_rating=10,
                    average_quality_rating=10)
        mixer.blend('videos.Video', pk=6, status="IN", link="6QwgLSVtYvG", average_interest_rating=9,
                    average_quality_rating=8)
        mixer.blend('videos.Video', pk=7, status="IN", link="7QwgLSVtYvG", average_interest_rating=2,
                    average_quality_rating=7)
        mixer.blend('videos.Video', pk=8, status="IN", link="8QwgLSVtYvG", average_interest_rating=8.45,
                    average_quality_rating=2.80)
        mixer.blend('videos.Video', pk=9, status="IN", link="9QwgLSVtYvG", average_interest_rating=7,
                    average_quality_rating=9)
        mixer.blend('videos.Video', pk=10, status="IN", link="10wgLSVtYvG", average_interest_rating=7.83,
                    average_quality_rating=10)

        video = VideoManager()
        result = video.getting_top_videos(req)

        assert result[0].get("video_link") == "5QwgLSVtYvG"
        assert result[1].get("video_link") == "6QwgLSVtYvG"
        assert result[2].get("video_link") == "8QwgLSVtYvG"
        assert result[3].get("video_link") == "10wgLSVtYvG"
        assert result[4].get("video_link") == "9QwgLSVtYvG"

    def test_getting_top_videos_with_less_than_5_rated_videos(self):
        # ##############################################################################################################
        # Scenario where the DB is populated with less than 5 videos rated
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        # We populate the DB in order for the function to be able to randomly select an item from
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=2, status="IN", link="2QwgLSVtYvG", average_interest_rating=6,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=3, status="OF", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=4, status="IN", link="4QwgLSVtYvG", average_interest_rating=None,
                    average_quality_rating=None)

        video = VideoManager()
        result = video.getting_top_videos(req)

        assert result[0].get("video_link") == "2QwgLSVtYvG"
        assert result[1].get("video_link") == "1QwgLSVtYvG"
        assert result[2].get("video_link") == "4QwgLSVtYvG"