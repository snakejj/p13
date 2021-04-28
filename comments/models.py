import hashlib
import os
from django.contrib import messages
from dotenv import load_dotenv, find_dotenv
from django.db import models

from videos.models import Video
load_dotenv(find_dotenv())


class CommentManager(models.Manager):
    def get_captcha_int(self):
        """
        Gets a captcha integer of length 4 or 5, based on the hash of the latest message posted and the hash of a
        secret key in a .env file.

        """

        captcha_key = os.getenv("CAPTCHA_SECRET_KEY")
        captcha_key_encoded = hashlib.sha256(captcha_key.encode('utf-8'))
        captcha_key_hashed = captcha_key_encoded.hexdigest()

        last_comment_message_raw = Comment.objects.latest('pk')
        last_comment_message = last_comment_message_raw.message
        last_comment_message_encoded = hashlib.sha256(last_comment_message.encode('utf-8'))
        last_comment_message_hashed = last_comment_message_encoded.hexdigest()

        captcha_int = str()
        i = 0
        while len(captcha_int) < 4:
            a = captcha_key_hashed[i]
            b = last_comment_message_hashed[i]
            if a.isdigit():
                c = int(a) + i
                captcha_int += str(c)
            if b.isdigit():
                c = int(b) + i
                captcha_int += str(c)
            i += 1

        return captcha_int

    def list_comments(self,request):
        try:
            video = request.session['video_pk']
            comments = Comment.objects.filter(video=video)
        except KeyError:
            comments = None

        return comments

    def submit_comment(self, request, comment_form):
        if comment_form.is_valid():
            pseudo = comment_form.data.get('comment-pseudo')
            email = comment_form.data.get('comment-email')
            message = comment_form.data.get('comment-message')
            video = Video.objects.get(pk=comment_form.data.get('video'))

            Comment.objects.create(video=video, pseudo=pseudo, email=email, message=message)
            messages.success(request, "Votre commentaire à bien été ajouté", fail_silently=True)
            return True
        else:
            return False


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

    objects = CommentManager()

