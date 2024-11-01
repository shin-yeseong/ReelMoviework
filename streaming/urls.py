# streaming/urls.py
from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    path('api/movies/', views.StreamingMovieList.as_view(), name='movie-list'),
    path('api/movies/<int:movie_id>/stream/', views.StreamVideo.as_view(), name='movie-stream'),
]