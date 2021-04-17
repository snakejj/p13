from django import forms


class LinkForm(forms.Form):
    link_submitted = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Soumettez vos liens YouTube les plus intéressants ici'}
        ),
    )
