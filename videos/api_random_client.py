import os
from random import randrange

import requests
from django.contrib import messages
from django.db.models import Q

from videos.models import Video


class ApiRandomOrg:

    def __init__(self):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        self.url = "https://api.random.org/json-rpc/4/invoke"

    def get_api_usage(self, request):
        data = {
            "jsonrpc": "2.0",
            "method": "getUsage",
            "params": {
                "apiKey": os.getenv("RANDOM_API_KEY")
            },
            "id": 15998
        }

        try:
            response = requests.post(self.url, json=data, headers=self.headers, timeout=5)

        except (requests.exceptions.ConnectionError, requests.Timeout):
            response = None

        api_daily_limit = int(os.getenv("API_DAILY_LIMIT"))

        if response is None or response.status_code != 200:
            # If there is an error with the API answer, we assign None to request_left

            messages.info(
                request,
                "L'API de randomisation etant indisponible, il est impossible d'avoir le nombre de requetes restante",
                fail_silently=True
            )
            nb_requests_used = None
        else:
            # If the API answer, we assign the API result to requests_left
            requests_left = response.json()["result"]["requestsLeft"]
            nb_requests_used = api_daily_limit - requests_left

        return nb_requests_used, api_daily_limit

    def select_random_video(self, request):
        # We count the number of videos still online
        max_pk = len(Video.objects.filter(~Q(status="OF")))

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
            response = requests.post(self.url, json=data, headers=self.headers, timeout=5)

        except (requests.exceptions.ConnectionError, requests.Timeout):
            response = None
            # raise requests.exceptions.ConnectionError("L'API de randomisation est indisponible")

        if response is None or response.status_code != 200:
            # If there is an error with the API answer, we use a pseudo-random integer
            random_pk = randrange(0, max_pk-1)
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
                messages.success(
                    request,
                    "L'API de randomisation a répondu en " + str(round(response.elapsed.total_seconds(), 2)) +
                    " secondes",
                    fail_silently=True
                )

            except KeyError:
                # if the result key does not exist, it means there is an error in the request,
                # if this message error, it means it is the first uploaded video and we need to manualy assign random_pk
                if "Parameter 'min' must be less than parameter 'max'" in response.json()["error"]["message"]:
                    random_pk = 0
                    videos_list = Video.objects.filter(~Q(status="OF"))
                    video = videos_list[random_pk]

                    messages.info(
                        request,
                        "Il n'y a pour l'instant qu'une seule video en base de données",
                        fail_silently=True
                    )
                    # raise KeyError("KeyError")

        return video.pk, video.link,