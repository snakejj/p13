import os
import json
from random import randrange

import requests
from django.contrib import messages
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from django.http import HttpResponseRedirect
from dotenv import load_dotenv, find_dotenv
from django.db import models
from urllib.parse import urlparse, parse_qs
import videos


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
            if len(clean) == 11 :
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
        try:
            Video.objects.get(link=clean_link)
            return False
            # Video.objects.get_or_create(link=clean_link)
        except videos.models.Video.DoesNotExist:
            Video.objects.create(link=clean_link)
            messages.success(request, "Votre vidéo à bien été ajouté en base de données", fail_silently=True)
            return True

    def select_random_video(self, request):
        # We count the number of videos still online
        max_pk = len(Video.objects.filter(~Q(status="OF")))

        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        url = "https://api.random.org/json-rpc/4/invoke"

        data = {
            "jsonrpc": "2.0",
            "method": "generateIntegers",
            "params": {
                "apiKey": os.getenv("RANDOM_API_KEY"),
                "n": 1,
                "min": 0,
                "max": max_pk - 1,
                "replacement": True
            },
            "id": 42
        }

        try:
            response = requests.post(url, json=data, headers=headers)
        except requests.exceptions.ConnectionError:
            response = None
        if response is None or response.status_code != 200:
            # If there is an error with the API answer, we use a pseudo-random integer
            random_pk = randrange(0,max_pk-1)
            videos_list = Video.objects.filter(~Q(status="OF"))
            video = videos_list[random_pk]

            messages.info(
                request,
                "L'API de randomisation etant indisponible, la vidéo a été généré pseudo aléatoirement",
                fail_silently=True
            )

        else:
            try:
                # If the API answer, we use a Truly random integer
                random_pk = response.json()["result"]["random"]["data"][0]
                videos_list = Video.objects.filter(~Q(status="OF"))
                video = videos_list[random_pk]

            except KeyError:
                # if the result key does not exist, it means there is an error in the request,

                # if this message error, it means it is the first uploaded video and we need to manualy assign random_pk
                if "Parameter 'min' must be less than parameter 'max'" in response.json()["error"]["message"]:
                    random_pk = 0
                    videos_list = Video.objects.filter(~Q(status="OF"))
                    video = videos_list[random_pk]

                    messages.info(
                        request,
                        "Bravo, vous venez d'uploader la premiere vidéo",
                        fail_silently=True
                    )

        return video.pk, video.link,

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
        else:
            messages.error(
                request, "Le lien est incorrect, merci de founir un lien Youtube valide", fail_silently=True
            )

    def submit_report_video(self, request, report_form):
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
                AbuseVideo.objects.create(video=video,reason=reason, message=message)
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
        else:
            messages.error(
                request, "Une erreur s'est produite", fail_silently=True
            )

    def generate_share_link(self, request, video_link):

        if "top-video" in request.path:
            video_link = request.session['top_video']

        base_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), request.path)

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
            for value in raw_data.values():
                full_link = "#"
                social_links[full_link] = value[1]

        return social_links

    def submit_rating_video(self, request, rating_form):
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
        else:
            messages.error(
                request, "Une erreur s'est produite", fail_silently=True
            )
            return False

    def getting_top_videos(self, request):
        list_of_videos_sorted_by_ratings = Video.objects.filter(
            ~Q(
                status="OF",
            ),
            ~Q(
                average_interest_rating=None,
            )
        ).order_by('-average_interest_rating', '-average_quality_rating')

        top_5_videos_raw = list_of_videos_sorted_by_ratings[:5]

        base_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), request.path)

        top_5_videos = []

        i = 1
        for value in top_5_videos_raw:
            top_5_videos.append(
                {
                    "video_rank": i,
                    "video_link": value.link,
                    "full_link": base_url + "?video_link=" + value.link,
                    "average_interest": value.average_interest_rating,
                    "average_quality": value.average_quality_rating,
                }
            )
            i += 1

        return top_5_videos

class Video(models.Model):
    link = models.CharField(max_length=11)
    added_on = models.DateTimeField(auto_now_add=True)

    INITIAL = 'IN'
    REPORTED = 'RE'
    ON = 'ON'
    OFF = 'OF'
    STATUS_CHOICES = [
        (INITIAL, 'initial'),
        (REPORTED, 'reported'),
        (ON, 'on'),
        (OFF, 'off'),
    ]

    average_interest_rating = models.DecimalField(
        null=True,
        max_digits=4,
        decimal_places=2,
    )

    average_quality_rating = models.DecimalField(
        null=True,
        max_digits=4,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=INITIAL,
    )

    objects = VideoManager()


class AbuseVideo(models.Model):
    video = models.ForeignKey(Video, related_name="abuse_video", on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    DEAD = 'D'
    ADULT = 'A'
    VIOLENT = 'V'
    FALSE = 'F'
    OTHER = 'O'
    REASON_CHOICES = [
        (DEAD, 'dead link'),
        (ADULT, 'adult content'),
        (VIOLENT, 'violent content'),
        (FALSE, 'false information'),
        (OTHER, 'other'),
    ]

    reason = models.CharField(
        max_length=1,
        choices=REASON_CHOICES,
        default=DEAD,
    )

    objects = VideoManager()


class RateVideo(models.Model):
    video = models.ForeignKey(Video, related_name="rate_video", on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    RATING_CHOICES = [
        (1, '1/10'),
        (2, '2/10'),
        (3, '3/10'),
        (4, '4/10'),
        (5, '5/10'),
        (6, '6/10'),
        (7, '7/10'),
        (8, '8/10'),
        (9, '9/10'),
        (10, '10/10'),
    ]

    interest_rating = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ],
        choices=RATING_CHOICES,
    )

    quality_rating = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ],
        choices=RATING_CHOICES,
    )

    objects = VideoManager()