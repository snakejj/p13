import hashlib
import os
from django.contrib import messages
from dotenv import load_dotenv, find_dotenv
from django.db import models
import comments
from videos.models import Video
load_dotenv(find_dotenv())


class CommentManager(models.Manager):

    def encrypt(self, captcha_int):
        # Using Vegenere encryption, with the key locate in .env

        key = str(os.getenv("CAPTCHA_SECRET_KEY"))
        captcha_int = str(captcha_int)

        key_list = []
        captcha_list = []
        for number in key:
            key_list.append(int(number))
        for number in captcha_int:
            captcha_list.append(int(number))

        i = 0
        mod = 10
        encrypted_captcha_list = []
        while i < 4:
            addition = key_list[i] + captcha_list[i]
            encrypted_number = addition % mod
            encrypted_captcha_list.append(encrypted_number)
            i += 1

        encrypted_captcha = str(encrypted_captcha_list).strip("[]").replace(", ", "")
        return encrypted_captcha

    def decrypt(self, encrypted_captcha):
        # Using Vegenere decryption, with the key locate in .env

        key = str(os.getenv("CAPTCHA_SECRET_KEY"))
        encrypted_captcha = str(encrypted_captcha)

        key_list = []
        encrypted_captcha_list = []
        for number in key:
            key_list.append(int(number))
        for number in encrypted_captcha:
            encrypted_captcha_list.append(int(number))

        i = 0
        mod = 10
        decrypted_captcha_list = []
        while i < 4:
            subtraction = encrypted_captcha_list[i] - key_list[i]
            decrypted_number = subtraction % mod
            decrypted_captcha_list.append(decrypted_number)
            i += 1

        decrypted_captcha = str(decrypted_captcha_list).strip("[]").replace(", ", "")
        return decrypted_captcha

    def get_hashed_value(self, value_to_hash):
        value_to_hash_encoded = hashlib.sha256(value_to_hash.encode('utf-8'))
        value_to_hash_hashed = value_to_hash_encoded.hexdigest()
        return value_to_hash_hashed

    def get_captcha_int(self, request, forcing_new_captcha):
        """
        Gets a captcha integer of length 4, based on the hash of the latest message posted and the hash of a
        secret key in a .env file.
        """

        temp_var_session_value = []
        for key, value in request.session.items():
            if key == "temp_var":
                temp_var_session_value.append(value)

        if not temp_var_session_value or forcing_new_captcha is True:

            captcha_key_hashed = self.get_hashed_value(os.getenv("CAPTCHA_SECRET_KEY"))

            try:
                last_comment_message_raw = Comment.objects.latest('pk')
                last_comment_message = last_comment_message_raw.message
                last_comment_message_hashed = self.get_hashed_value(last_comment_message)
            except comments.models.Comment.DoesNotExist:
                last_comment_message = "Random message in case there is no comment yet"
                last_comment_message_hashed = self.get_hashed_value(last_comment_message)

            captcha_int = str()
            i = 0
            while len(captcha_int) < 4:
                a = captcha_key_hashed[i]
                b = last_comment_message_hashed[i]
                if a.isdigit():
                    c = int(a) + i
                    captcha_int += str(c)
                if b.isdigit() and len(captcha_int) < 4:
                    c = int(b) + i
                    captcha_int += str(c)
                i += 1

            # This part is to avoid getting a captcha error if in the meantime someone else has posted a comment.
            # We store in a variable the result of get_captcha_int(), encrypted, so that it is the same for the user

            request.session['temp_var'] = self.encrypt(captcha_int)
            return request.session['temp_var']

    def list_comments(self, request):
        if "top-videos" in request.path:
            try:
                video = request.session['top_video_pk']
                comments = Comment.objects.filter(video=video)
            except KeyError:
                comments = None
        elif "video-aleatoire" in request.path:
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
        # else:
        #     return False


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
