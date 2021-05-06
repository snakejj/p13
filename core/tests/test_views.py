import json

import pytest

import requests
from django import urls
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from requests.exceptions import ConnectionError
import responses

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, Client, TestCase
from mixer.backend.django import mixer

import videos
from core.views import home
from core import views

from videos.forms import LinkForm
from videos.models import VideoManager

pytestmark = pytest.mark.django_db


def test_if_home_view_is_working():
    req = RequestFactory().get('/')
    resp = views.home(req)

    assert resp.status_code == 200, 'Should display the home page'


def test_if_legal_notice_view_is_working():
    req = RequestFactory().get('/')
    resp = views.legal_notice(req)

    assert resp.status_code == 200, 'Should display the legal_notice page'