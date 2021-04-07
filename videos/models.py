from django.db import models
from urllib.parse import urlparse, parse_qs


class VideoManager(models.Manager):

    def _parse_link(self, raw_link):
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
        # fail?
        return None

    def _add_video(self, clean_link):
        pass

    def _change_status(self, video_id, desired_status):
        pass

    def _select_random_video(self):
        pass



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
