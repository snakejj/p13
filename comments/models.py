from django.db import models
from comments import managers
from videos.models import Video


class Comment(models.Model):

    video = models.ForeignKey(Video, related_name="comments", on_delete=models.CASCADE)
    pseudo = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    message = models.TextField()
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

    class Meta:
        ordering = ['-added_on']

    objects = managers.CommentManager()
