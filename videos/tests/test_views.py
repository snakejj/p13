import pytest
from django import urls
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.test import RequestFactory
from mixer.backend.django import mixer
from videos import views
pytestmark = pytest.mark.django_db


class TestTopVideosView:

    def test_if_view_top_videos_work_with_top_video_variable_yet_and_db_not_empty(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=2, status="IN", link="2QwgLSVtYvG", average_interest_rating=6,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=3, status="OF", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=4, status="IN", link="4QwgLSVtYvG", average_interest_rating=None,
                    average_quality_rating=None)

        request = RequestFactory().get('/top-videos/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_unique_video'] = True
        request.session['has_submit_vote'] = ["VPkbtMLzeoc"]
        request.session['has_submit_report'] = ["VPkbtMLzsoc"]
        request.session['top_video'] = "3QwgLSVtYvG"
        request.session.save()

        resp = views.top_videos(request)

        assert resp.status_code == 200, ''
        assert '<iframe src="https://www.youtube.com/embed/3QwgLSVtYvG"' in str(resp.getvalue()), ''

    @pytest.mark.xfail(raises=KeyError)
    def test_if_view_top_videos_work_with_no_top_video_variable_yet_and_db_empty(self):
        request = RequestFactory().get('/top-videos/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        resp = views.top_videos(request)

        assert resp.status_code == 200, ''
        assert "Pour acceder" in str(resp.getvalue()), 'Should return the text inviting to submit a video'

    @pytest.mark.xfail(raises=KeyError)
    def test_if_view_top_videos_work_with_no_top_video_variable_yet_and_db_not_empty(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=2, status="IN", link="2QwgLSVtYvG", average_interest_rating=6,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=3, status="OF", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)
        mixer.blend('videos.Video', pk=4, status="IN", link="4QwgLSVtYvG", average_interest_rating=None,
                    average_quality_rating=None)

        request = RequestFactory().get('/top-videos/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_unique_video'] = True
        request.session.save()

        resp = views.top_videos(request)

        assert resp.status_code == 200, ''
        assert '<iframe src="https://www.youtube.com/embed/2QwgLSVtYvG"' in str(resp.getvalue()), ''

    def test_if_view_top_videos_work_when_choosing_an_other_top_video_that_exists(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        request = RequestFactory().get('/top-videos/?video_link=1QwgLSVtYvG')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_unique_video'] = True
        request.session.save()

        resp = views.top_videos(request)

        assert resp.status_code == 200, ''
        assert '<iframe src="https://www.youtube.com/embed/1QwgLSVtYvG"' in str(resp.getvalue()), ''

    @pytest.mark.xfail(raises=IndexError)
    def test_if_view_top_videos_work_when_choosing_an_other_top_video_that_does_not_exists(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        request = RequestFactory().get('/top-videos/?video_link=1QwgLvVtYvG')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_unique_video'] = True
        request.session.save()

        resp = views.top_videos(request)

        assert resp.status_code == 200, ''
        assert '<iframe src="https://www.youtube.com/embed/1QwgLvVtYvG" ' in str(resp.getvalue()), ''

    def test_if_view_top_videos_work_with_posting_report(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        data = {
                'report-reason': "V",
                'report-message': "Random message",
                'video': "1",
                'report_sent': "",
            }

        url = reverse('videos:top_videos')
        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session.save()

        resp = views.top_videos(post_request)

        assert resp.status_code == 302, ''
        assert resp.url == urls.reverse('videos:top_videos'), ''

    def test_if_view_top_videos_work_with_posting_comment_with_incorrect_captcha(self):
        # We populate the DB
        video_instance = mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG",
                                     average_interest_rating=4.50, average_quality_rating=3.30)
        mixer.blend('comments.Comment', video=video_instance)

        data = {
                'comment-pseudo': "pseudo",
                'comment-email': "email@dadzds.com",
                'comment-message': "my unposted message waiting for second captcha try",
                'captcha': "",
                'video': "1",
                'comment_sent': "",
            }

        url = reverse('videos:top_videos')

        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['has_submit_unique_video'] = True
        post_request.session['video_pk'] = 1
        post_request.session.save()

        resp = views.top_videos(post_request)

        assert resp.status_code == 200, ''
        assert "my unposted message waiting for second captcha try" in str(resp.getvalue()), ''

    def test_if_view_top_videos_work_with_posting_comment_with_correct_captcha(self):
        # We populate the DB
        video_instance = mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG",
                                     average_interest_rating=4.50, average_quality_rating=3.30)
        mixer.blend('comments.Comment', video=video_instance)

        data = {
                'comment-pseudo': "pseudo",
                'comment-email': "email@dadzds.com",
                'comment-message': "my posted message after a getting the captcha right",
                'captcha': "7666",  # This is the uncrypted value of "1234" using comments.models.decrypt()
                'video': "1",
                'comment_sent': "",
            }

        url = reverse('videos:top_videos')

        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['has_submit_unique_video'] = True
        post_request.session['video_pk'] = 1
        post_request.session['temp_var'] = "1234"
        post_request.session.save()

        resp = views.top_videos(post_request)
        assert resp.status_code == 302, 'If captcha is correct, it should redirect to the same page'
        assert resp.url == urls.reverse('videos:top_videos'), ''


class TestRandomVideosView:
    def test_if_view_random_video_work_with_user_having_variables_has_submit_report_and_has_submit_vote(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=2, status="IN", link="2QwgLSVtYvG", average_interest_rating=6,
                    average_quality_rating=3.30)

        request = RequestFactory().get('/video-aleatoire/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['has_submit_vote'] = ["2QwgLSVtYvG"]
        request.session['has_submit_report'] = ["2QwgLSVtYvG"]
        request.session['has_submit_unique_video'] = True
        request.session['video_link'] = "2QwgLSVtYvG"
        request.session.save()

        resp = views.random_video(request)
        assert resp.status_code == 200, ''
        assert '<iframe src="https://www.youtube.com/embed/2QwgLSVtYvG"' in str(resp.getvalue()), ''
        assert 'Votre signalement a bien' in str(resp.getvalue()), 'Should say that the report has been saved already'
        assert 'Vous avez deja vot' in str(resp.getvalue()), 'Should say that the user already voted this video'

    @pytest.mark.xfail(raises=KeyError)
    def test_if_view_random_video_work_with_a_shared_link_which_exists_in_db(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=3, status="IN", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)

        request = RequestFactory().get('/video-aleatoire/?video_link=3QwgLSVtYvG')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        resp = views.random_video(request)

        assert resp.status_code == 200, ''
        assert '<iframe src="https://www.youtube.com/embed/3QwgLSVtYvG"' in str(resp.getvalue()), ''

    @pytest.mark.xfail(raises=IndexError)
    def test_if_view_random_video_work_with_a_shared_link_which_doesnt_exists_in_db(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=3, status="IN", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)

        request = RequestFactory().get('/video-aleatoire/?video_link=0QwgLSVtYvG')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        resp = views.random_video(request)

        assert resp.status_code == 302, 'Should redirect to the home page if link is incorrect'
        assert resp.url == urls.reverse('core:home'), ''

    @pytest.mark.xfail(raises=IndexError)
    def test_if_view_random_video_work_with_a_shared_link_which_is_moderated_offline(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=3, status="OF", link="3QwgLSVtYvG", average_interest_rating=2.20,
                    average_quality_rating=3.30)

        request = RequestFactory().get('/video-aleatoire/?video_link=3QwgLSVtYvG')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        resp = views.random_video(request)

        assert resp.status_code == 302, 'Should redirect to the home page if link is incorrect'

    def test_if_view_random_video_work_with_posting_report(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        data = {
                'report-reason': "V",
                'report-message': "Random message",
                'video': "1",
                'report_sent': "",
            }

        url = reverse('videos:random_video')
        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['video_link'] = "1QwgLSVtYvG"
        post_request.session.save()

        resp = views.random_video(post_request)

        assert resp.status_code == 302, ''
        assert resp.url == urls.reverse('videos:random_video'), ''

    def test_if_view_random_video_work_with_posting_rating(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        data = {
                'rate-interest': 3,
                'rate-quality': 7,
                'video': "1",
                'rating_sent': "",
            }

        url = reverse('videos:random_video')
        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['video_link'] = "1QwgLSVtYvG"
        post_request.session.save()

        resp = views.random_video(post_request)

        assert resp.status_code == 302, ''
        assert resp.url == urls.reverse('videos:random_video')
        assert "1QwgLSVtYvG" in post_request.session['has_submit_vote'], \
            "the 'has_submit_vote' should contain the rated video's link"

    def test_if_view_random_work_with_posting_report(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        data = {
                'report-reason': "V",
                'report-message': "Random message",
                'video': "1",
                'report_sent': "",
            }

        url = reverse('videos:random_video')
        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['video_link'] = "1QwgLSVtYvG"
        post_request.session.save()

        resp = views.random_video(post_request)

        assert resp.status_code == 302, ''
        assert resp.url == urls.reverse('videos:random_video')
        assert "1QwgLSVtYvG" in post_request.session['has_submit_report'], \
            "the 'has_submit_report' should contain the rated video's link"

    def test_if_view_random_video_work_with_posting_comment_with_incorrect_captcha(self):
        # We populate the DB
        video_instance = mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG",
                                     average_interest_rating=4.50, average_quality_rating=3.30)
        mixer.blend('comments.Comment', video=video_instance)

        data = {
                'comment-pseudo': "pseudo",
                'comment-email': "email@dadzds.com",
                'comment-message': "my unposted message waiting for second captcha try",
                'captcha': "",
                'video': "1",
                'comment_sent': "",
            }

        url = reverse('videos:random_video')

        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['has_submit_unique_video'] = True
        post_request.session['video_pk'] = 1
        post_request.session.save()

        resp = views.random_video(post_request)

        assert resp.status_code == 200, ''
        assert "my unposted message waiting for second captcha try" in str(resp.getvalue()), ''

    def test_if_view_random_video_work_with_posting_comment_with_correct_captcha(self):
        # We populate the DB
        video_instance = mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG",
                                     average_interest_rating=4.50, average_quality_rating=3.30)
        mixer.blend('comments.Comment', video=video_instance)

        data = {
                'comment-pseudo': "pseudo",
                'comment-email': "email@dadzds.com",
                'comment-message': "my posted message after a getting the captcha right",
                'captcha': "7666",  # This is the uncrypted value of "1234" using comments.models.decrypt()
                'video': "1",
                'comment_sent': "",
            }

        url = reverse('videos:random_video')

        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session['has_submit_unique_video'] = True
        post_request.session['video_pk'] = 1
        post_request.session['temp_var'] = "1234"
        post_request.session.save()

        resp = views.random_video(post_request)
        assert resp.status_code == 302, 'If captcha is correct, it should redirect to the same page'
        assert resp.url == urls.reverse('videos:random_video'), ''

    def test_if_view_random_video_work_with_posting_a_valid_new_video_link(self):
        # We populate the DB
        mixer.blend('videos.Video', pk=1, status="IN", link="1QwgLSVtYvG", average_interest_rating=4.50,
                    average_quality_rating=3.30)

        data = {
                'video-link': "http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu",
                'link_sent': "",
            }

        url = reverse('videos:random_video')

        request = RequestFactory()
        post_request = request.post(url, data=data)
        middleware = SessionMiddleware()
        middleware.process_request(post_request)
        post_request.session.save()

        resp = views.random_video(post_request)
        assert resp.status_code == 302, 'If link is correct, it should redirect to the same page'
        assert resp.url == urls.reverse('videos:random_video'), ''
        assert post_request.session['has_submit_unique_video'] is True, \
            "the 'has_submit_unique_video' should return True if video's link has been submited and is correct"
