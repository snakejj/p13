import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from mixer.backend.django import mixer
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
