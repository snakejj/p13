import pytest
from django import urls
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from mixer.backend.django import mixer
from users import views
pytestmark = pytest.mark.django_db


def test_if_dashboard_view_is_not_working_when_not_connected():
    req = RequestFactory().get('/admin/')
    resp = views.dashboard(req)

    assert "cette page vous devez etre connec" in str(resp.getvalue()), \
        'Should display message saying that in order to display this page you must be connected'


def test_if_dashboard_view_is_working_when_connected():
    admin = mixer.blend('auth.User', id=1)
    req = RequestFactory().get('/admin/')
    req.user = admin
    resp = views.dashboard(req)

    assert "Tableau de bord" in str(resp.getvalue()), \
        'Should display the dashboard'


def test_if_logout_view_is_working():
    admin = mixer.blend('auth.User', id=1)
    request = RequestFactory().get('/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.user = admin
    request.session.save()

    resp = views.logout(request)
    assert resp.status_code == 302, 'Should redirect to the home page'
    assert request.user == AnonymousUser(), 'The user should be AnonymousUser'


@pytest.mark.django_db
def test_if_login_view_is_working_with_improper_password(client):

    # Create a fake user
    user = mixer.blend('auth.User', username='my_username')
    user.set_password('my_password123')
    user.save()

    login_url = urls.reverse('users:login')
    resp = client.post(login_url, {
        'username': 'my_username',
        'password': 'improper_password'
    })

    assert resp.status_code == 200, 'Should refresh the page'
    assert not Session.objects.exists(), 'Should not be any session if login failed'


@pytest.mark.django_db
def test_if_login_view_is_working_with_improper_user(client):

    # Create a fake user
    user = mixer.blend('auth.User', username='my_username')
    user.set_password('my_password123')
    user.save()

    login_url = urls.reverse('users:login')
    resp = client.post(login_url, {
        'username': 'my_username_error',
        'password': 'my_password123'
    })

    assert resp.status_code == 200, 'Should refresh the page'
    assert not Session.objects.exists(), 'Should not be any session if login failed'


@pytest.mark.django_db
def test_if_login_view_is_working_with_proper_credentials(client):

    # Create a fake user
    user = mixer.blend('auth.User', username='my_username', is_active='True')
    user.set_password('my_password123')
    user.save()

    login_url = urls.reverse('users:login')
    resp = client.post(login_url, {
        'username': 'my_username',
        'password': 'my_password123'
    })

    assert resp.status_code == 302 and resp.url == urls.reverse('users:dashboard'), \
        'Should redirect to the dashboard page'
    assert Session.objects.count() == 1, 'Should create a session for the logged in users'


@pytest.mark.django_db
def test_if_login_view_is_working_with_proper_credentials_but_inactive(client):

    # Create a fake user
    user = mixer.blend('auth.User', username='my_username', is_active='False')
    user.set_password('my_password123')
    user.save()

    login_url = urls.reverse('users:login')
    resp = client.post(login_url, {
        'username': 'my_username',
        'password': 'my_password123'
    })

    assert resp.status_code == 302 and resp.url == urls.reverse('users:login'), 'Should redirect to the login page'
    assert Session.objects.count() == 0, 'Should not create a session for the logged in users'
