from django import forms

from videos.models import Video


class LinkForm(forms.Form):

    link = forms.CharField(
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