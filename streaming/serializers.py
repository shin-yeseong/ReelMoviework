# streaming/serializers.py
from rest_framework import serializers
from .models import StreamingMovie

class StreamingMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingMovie
        fields = ['id', 'title', 'genre', 'time', 'summary', 'creator', 'release_date', 'views']