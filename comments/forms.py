from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    pseudo = forms.CharField(
        label='pseudo',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': "Pseudo",
                'id': "pseudo-input",
                "max_length": 100,
            }
        )
    )
    email = forms.EmailField(
        label='email',
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'placeholder': "Email",
                'id': "email-input",
                "max_length": 254,
            }
        )
    )
    message = forms.CharField(
        label='message',
        widget=forms.Textarea(
            attrs={
                'placeholder': "Message",
                'id': "message-input",
            }
        )
    )

    class Meta:
        model = Comment
        fields = ["pseudo", "email", "message"]


class CaptchaForm(forms.Form):
    captcha = forms.CharField(
        label='captcha',
        widget=forms.TextInput(
            attrs={
                'placeholder': "Captcha",
                'id': "captcha-input",
            }
        )
    )
