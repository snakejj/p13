from django import forms

from videos.models import Video, AbuseVideo, RateVideo


class LinkForm(forms.Form):

    link = forms.CharField(
        required=False,
        label='link_submitted',
        widget=forms.TextInput(
            attrs={
                'placeholder': "Soumettez vos liens YouTube les plus intéressants ici",
                'id': "link",
                "max_length": 100,
            }
        )
    )

    class Meta:
        model = Video
        fields = ["link"]


class ReportForm(forms.Form):

    REASON_CHOICES = [
        ("D", 'Lien mort'),
        ("A", 'Contenu adulte'),
        ("V", 'Contenu violent'),
        ("F", 'Fausse(s) information'),
        ("O", 'Autre'),
    ]

    reason = forms.ChoiceField(
        label='report',
        widget=forms.RadioSelect,
        choices=REASON_CHOICES,
    )

    message = forms.CharField(
        required=False,
        label='message',
        widget=forms.Textarea(
            attrs={
                'placeholder': "Merci de preciser ici, si necessaire",
                'id': "message-input",
            }
        )
    )

    class Meta:
        model = AbuseVideo
        fields = ["reason", "message"]


class RatingForm(forms.Form):

    interest = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': "Notez entre 0 et 10",
                'id': "interest",
                'name': "interest",
                'min': 0,
                'max': 10,

            }
        ),
    )

    quality = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': "Notez entre 0 et 10",
                'id': "quality",
                'name': "quality",
                'min': 0,
                'max': 10,

            }
        ),
    )

    class Meta:
        model = RateVideo
        fields = ["interest", "quality"]
