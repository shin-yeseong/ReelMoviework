# streaming/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse, Http404
from .models import StreamingMovie
from .serializers import StreamingMovieSerializer
import mimetypes
from django.shortcuts import render, redirect
from .forms import StreamingMovieForm
from django.contrib.auth.decorators import login_required
import uuid
import datetime
from mongodbconnect import settings


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

# streaming/views.py

# @login_required
def upload_streaming_movie(request):
    if request.method == 'POST':
        form = StreamingMovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie_data = {
                "_id": str(uuid.uuid4()),  # 고유 ID 생성
                "title": form.cleaned_data['title'],
                "genre": form.cleaned_data['genre'],
                "time": form.cleaned_data['time'],
                "summary": form.cleaned_data['summary'],
                "creator_id": str(request.user.id),  # 로그인한 사용자의 ID 저장
                "release_date": form.cleaned_data['release_date'],
                "streaming_url": form.cleaned_data['streaming_url'],
                "views": 0,
                "payment_history": [],
                "viewer": []
            }

            # MongoDB에 저장
            settings.mongo_db.streaming_movies.insert_one(movie_data)
            return redirect('streaming:streaming_movie_page')
    else:
        form = StreamingMovieForm()
    return render(request, 'upload_streaming.html', {'form': form})