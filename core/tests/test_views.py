import pytest
from django.test import RequestFactory
from core import views
pytestmark = pytest.mark.django_db


def test_if_home_view_is_working():
    req = RequestFactory().get('/')
    resp = views.home(req)

    assert resp.status_code == 200, 'Should display the home page'


def test_if_legal_notice_view_is_working():
    req = RequestFactory().get('/')
    resp = views.legal_notice(req)

    assert resp.status_code == 200, 'Should display the legal_notice page'
