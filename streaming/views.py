# streaming/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse, Http404
from .models import StreamingMovie
from .serializers import StreamingMovieSerializer
import mimetypes


class StreamingMovieList(APIView):
    def get(self, request):
        movies = StreamingMovie.objects.all()
        serializer = StreamingMovieSerializer(movies, many=True)
        return Response(serializer.data)


class StreamVideo(APIView):
    def get(self, request, movie_id):
        try:
            movie = StreamingMovie.objects.get(id=movie_id)
        except StreamingMovie.DoesNotExist:
            raise Http404("Video not found")

        file_path = movie.streaming_url.path
        file_mimetype, _ = mimetypes.guess_type(file_path)

        def file_iterator(file_name, chunk_size=8192):
            with open(file_name, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        response = StreamingHttpResponse(file_iterator(file_path), content_type=file_mimetype)
        response['Content-Length'] = movie.streaming_url.size
        response['Content-Disposition'] = f'inline; filename="{movie.title}.mp4"'
        return response