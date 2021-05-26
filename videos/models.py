from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from videos import managers


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

    objects = managers.VideoManager()


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

    report_dealt_with = models.BooleanField(
        default=False,
    )

    objects = managers.VideoManager()


class RateVideo(models.Model):
    video = models.ForeignKey(Video, related_name="rate_video", on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    RATING_CHOICES = [
        (0, '0/10'),
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

    objects = managers.VideoManager()
