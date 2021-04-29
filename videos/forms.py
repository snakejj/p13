from django import forms

from videos.models import Video, AbuseVideo


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