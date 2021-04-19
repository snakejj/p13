import os
import json
from random import randrange

import requests
from dotenv import load_dotenv, find_dotenv
from django.db import models
from urllib.parse import urlparse, parse_qs
import videos


load_dotenv(find_dotenv())


class VideoManager(models.Manager):
    def parse_link(self, request, raw_link):
        # Examples:
        # - http://youtu.be/SA2iWivDJiE
        # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        # - http://www.youtube.com/embed/SA2iWivDJiE
        # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        query = urlparse(raw_link)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in {'www.youtube.com', 'youtube.com'}:
            if query.path == '/watch':
                return parse_qs(query.query)['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        elif request.user.is_authenticated:
            return ""
        # fail?
        return False

    def add_video(self, request, clean_link):
        if len(clean_link) == 11:
            try:
                Video.objects.get(link=clean_link)
                return False
                # Video.objects.get_or_create(link=clean_link)
            except videos.models.Video.DoesNotExist:
                Video.objects.create(link=clean_link)
                return True
        elif request.user.is_authenticated:
            return "admin"
        else:
            return None

    def select_random_video(self):

        max_pk = len(Video.objects.filter())
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
                "min": 1,
                "max": max_pk,
                "replacement": True
            },
            "id": 42
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            # If the API answer, we use a Truly random integer
            random_pk = response.json()["result"]["random"]["data"][0]
            video = Video.objects.get(pk=random_pk)
            return video.link, True
        else:
            # If there is an error with the API answer, we use a pseudo-random integer
            random_pk = randrange(1,max_pk+1)
            video = Video.objects.get(pk=random_pk)
            return video.link, False


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

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=INITIAL,
    )

    objects = VideoManager()
