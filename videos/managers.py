from django.apps import apps
from django.db import models
from django import urls
from django.contrib import messages
from urllib.parse import urlparse, parse_qs
import videos
from django.db.models import Q, F
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class VideoManager(models.Manager):
    def _parse_link(self, request, raw_link):
        # Examples:
        # - http://youtu.be/SA2iWivDJiE
        # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        # - http://www.youtube.com/embed/SA2iWivDJiE
        # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        query = urlparse(raw_link)
        if query.hostname == 'youtu.be':
            clean = query.path[1:]
            if len(clean) == 11:
                return clean
        if query.hostname in {'www.youtube.com', 'youtube.com'}:
            if query.path == '/watch':
                clean = parse_qs(query.query)['v'][0]
                if len(clean) == 11:
                    return clean
            if query.path[:7] == '/embed/':
                clean = query.path.split('/')[2]
                if len(clean) == 11:
                    return clean
            if query.path[:3] == '/v/':
                clean = query.path.split('/')[2]
                if len(clean) == 11:
                    return clean
        elif request.user.is_authenticated:
            return True
        # fail?
        return False

    def _add_video(self, request, clean_link):
        """

        :param request:
        :param clean_link:
        :return
        -False (if video exist already in DB)
        -True (if video did not existed and was successfully inserted in DB)
        :


        """
        Video = apps.get_model(app_label='videos', model_name='Video')

        try:
            Video.objects.get(link=clean_link)
            return False
            # Video.objects.get_or_create(link=clean_link)
        except videos.models.Video.DoesNotExist:
            Video.objects.create(link=clean_link)
            messages.success(request, "Votre vidéo à bien été ajouté en base de données", fail_silently=True)
            return True

    def submit_video(self, request, link_form):
        if link_form.is_valid():
            link = link_form.data.get('video-link')

            clean_link = self._parse_link(request, link)
            if type(clean_link) is not bool:
                video_is_unique = self._add_video(request, clean_link)
                if video_is_unique is True:
                    request.session['has_submit_unique_video'] = True

                elif video_is_unique is False:
                    messages.warning(
                        request, "La vidéo à deja été proposé, merci de proposer une autre vidéo", fail_silently=True
                    )
                return video_is_unique

            # if admin is connected :
            elif clean_link is True:
                request.session['has_submit_unique_video'] = True
                return True

            elif clean_link is False:
                messages.error(
                    request, "Le lien est incorrect, merci de founir un lien Youtube valide", fail_silently=True
                )
        # else:
        #     messages.error(
        #         request, "Le lien est incorrect, merci de founir un lien Youtube valide", fail_silently=True
        #     )

    def generate_share_link(self, request, video_link):
        if "top-video" in request.path:
            video_link = request.session['top_video']

        base_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), urls.reverse('videos:random_video'))

        raw_data = {
            "facebook_url": ["https://www.facebook.com/sharer/sharer.php?u=", "fab fa-facebook-square fa-2x"],
            "twitter_url": ["https://twitter.com/intent/tweet?url=", "fab fa-twitter-square fa-2x"],
            "linked_url": ["http://www.linkedin.com/shareArticle?mini=true&url=", "fab fa-linkedin fa-2x"],
            "whatsapp_url": ["https://api.whatsapp.com/send?text=", "fab fa-whatsapp-square fa-2x"],
            "telegram_url": ["https://telegram.me/share/url?url=", "fab fa-telegram-plane fa-2x"],
            "email_url": ["mailto:%7Bemail_address%7D?subject=&body=", "fa fa-envelope fa-2x"],
        }

        social_links = dict()

        try:
            for value in raw_data.values():
                full_link = value[0] + base_url + "?video_link=" + video_link
                social_links[full_link] = value[1]
        except TypeError:
            social_links = {}

        return social_links

    def getting_top_videos(self, request):
        Video = apps.get_model('videos', 'Video')

        list_of_videos_sorted_by_ratings = Video.objects.filter(
            ~Q(
                status="OF",
            ),
        ).order_by(
            F('average_interest_rating').desc(nulls_last=True),
            F('average_quality_rating').desc(nulls_last=True)
        )

        base_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), urls.reverse('videos:top_videos'))
        top_5_videos = []
        i = 1

        top_5_videos_raw = list_of_videos_sorted_by_ratings[:5]

        for value in top_5_videos_raw:
            if value.average_interest_rating is None:
                top_5_videos.append(
                    {
                        "video_rank": i,
                        "video_link": value.link,
                        "full_link": base_url + "?video_link=" + value.link,
                        "average_interest": "Pas encore noté",
                        "average_quality": "Pas encore noté",
                    }
                )
                i += 1
            else:
                top_5_videos.append(
                    {
                        "video_rank": i,
                        "video_link": value.link,
                        "full_link": base_url + "?video_link=" + value.link,
                        "average_interest": str(value.average_interest_rating) + "/10",
                        "average_quality": str(value.average_quality_rating) + "/10",
                    }
                )
                i += 1

        return top_5_videos

    def get_videos_count(self):
        Video = apps.get_model('videos', 'Video')

        count = Video.objects.all().count()
        url = "/superadminvideos/video/"
        all_videos = {
            'count': count,
            'url': url,

        }
        return all_videos


class AbuseVideoManager(models.Manager):
    def submit_report_video(self, request, report_form):
        Video = apps.get_model('videos', 'Video')
        AbuseVideo = apps.get_model('videos', 'AbuseVideo')

        if report_form.is_valid():
            video = Video.objects.get(pk=report_form.data.get('video'))
            reason = report_form.data.get('report-reason')
            message = report_form.data.get('report-message')

            if video.status == "ON":
                # Here we do not change the video's status as it was already moderated, still we save the report
                AbuseVideo.objects.create(video=video, reason=reason, message=message)
                messages.success(
                    request,
                    "Cette vidéo a été considéré conforme, "
                    "neamoins votre signalement a été enregistré pour un eventuel réexamen",
                    fail_silently=True
                )
                if "top-videos" in request.path:
                    list_of_reported_video = request.session['has_submit_report']
                    list_of_reported_video.append(request.session['top_video'])
                    request.session['has_submit_report'] = list_of_reported_video
                elif "video-aleatoire" in request.path:
                    list_of_reported_video = request.session['has_submit_report']
                    list_of_reported_video.append(request.session['video_link'])
                    request.session['has_submit_report'] = list_of_reported_video
            else:
                # Here we do change the video's status to "RE" ("reported")
                AbuseVideo.objects.create(video=video, reason=reason, message=message)
                messages.success(request, "Votre signalement a bien été enregistré", fail_silently=True)
                video.status = 'RE'
                video.save()

                if "top-videos" in request.path:
                    list_of_reported_video = request.session['has_submit_report']
                    list_of_reported_video.append(request.session['top_video'])
                    request.session['has_submit_report'] = list_of_reported_video
                elif "video-aleatoire" in request.path:
                    list_of_reported_video = request.session['has_submit_report']
                    list_of_reported_video.append(request.session['video_link'])
                    request.session['has_submit_report'] = list_of_reported_video
        # else:
        #     messages.error(
        #         request, "Une erreur s'est produite", fail_silently=True
        #     )

    def get_report_pending(self):
        AbuseVideo = apps.get_model('videos', 'AbuseVideo')

        count = AbuseVideo.objects.filter(report_dealt_with=False).count()
        url = "/superadminvideos/abusevideo/?report_dealt_with__exact=0"
        report_pending = {
            'count': count,
            'url': url,

        }
        return report_pending


class RateVideoManager(models.Manager):
    def submit_rating_video(self, request, rating_form):
        Video = apps.get_model('videos', 'Video')
        RateVideo = apps.get_model('videos', 'RateVideo')

        if rating_form.is_valid():
            video = Video.objects.get(pk=rating_form.data.get('video'))
            interest_rating = int(rating_form.data.get('rate-interest'))
            quality_rating = int(rating_form.data.get('rate-quality'))

            list_of_ratings_for_this_video = RateVideo.objects.filter(video=video)
            if len(list_of_ratings_for_this_video) > 0:
                list_interest_ratings = []
                list_quality_ratings = []
                for i in range(0, len(list_of_ratings_for_this_video)):
                    list_interest_ratings.append(list_of_ratings_for_this_video[i].quality_rating)
                    list_quality_ratings.append(list_of_ratings_for_this_video[i].interest_rating)

                list_interest_ratings.append(interest_rating)
                list_quality_ratings.append(quality_rating)

                average_interest_rating = sum(list_interest_ratings) / len(list_interest_ratings)
                average_quality_rating = sum(list_quality_ratings) / len(list_quality_ratings)
            else:
                average_interest_rating = interest_rating
                average_quality_rating = quality_rating

            try:
                list_of_rated_video = request.session['has_submit_vote']
                list_of_rated_video.append(request.session['video_link'])
                request.session['has_submit_vote'] = list_of_rated_video
            except KeyError:
                request.session['has_submit_vote'] = []
                list_of_rated_video = request.session['has_submit_vote']
                list_of_rated_video.append(request.session['video_link'])
                request.session['has_submit_vote'] = list_of_rated_video

            RateVideo.objects.create(
                video=video,
                interest_rating=interest_rating,
                quality_rating=quality_rating,
            )

            Video.objects.filter(pk=video.pk).update(
                average_interest_rating=average_interest_rating,
                average_quality_rating=average_quality_rating
            )
            messages.success(request, "Votre vote a bien été enregistré", fail_silently=True)
            return True

    def get_videos_rated_count(self):
        Video = apps.get_model('videos', 'Video')

        count = Video.objects.filter(~Q(average_interest_rating=None)).count()
        url = "/superadminvideos/video/?o=5"
        all_videos_rated = {
            'count': count,
            'url': url,

        }
        return all_videos_rated

    def get_rating_count(self):
        RateVideo = apps.get_model('videos', 'RateVideo')

        count = RateVideo.objects.all().count()
        url = "/superadminvideos/ratevideo/"
        all_rating = {
            'count': count,
            'url': url,

        }
        return all_rating
