# funding/forms.py
from django import forms
from .models import FundingMovie

class FundingMovieForm(forms.ModelForm):
    genre = forms.MultipleChoiceField(
        choices=[
            ('Action', 'Action'),
            ('Comedy', 'Comedy'),
            ('Drama', 'Drama'),
            ('SF', 'SF'),
            ('Romance', 'Romance'),
            ('Thriller', 'Thriller'),
            ('Horror', 'Horror'),
            ('Animation', 'Animation'),
            ('Crime', 'Crime'),
            ('Fantasy', 'Fantasy'),
            ('Adventure', 'Adventure'),
            ('ETC', 'ETC')
        ],
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = FundingMovie
        fields = [
            'title', 'genre', 'time', 'intention', 'summary', 'making_description',
            'target_funding', 'funding_description', 'funding_deadline',
            'creator', 'actors', 'creator_talk'
        ]
