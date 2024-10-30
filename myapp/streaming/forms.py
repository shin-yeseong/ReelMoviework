# streaming/forms.py
from django import forms
from .models import StreamingMovie

class StreamingMovieForm(forms.ModelForm):
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
        model = StreamingMovie
        fields = ['title', 'genre', 'time', 'summary', 'release_date', 'streaming_url']
