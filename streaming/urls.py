# streaming/urls.py
from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    path('upload/', views.upload_streaming_movie, name='upload_streaming_movie'),
    path('<int:movie_id>/', views.streaming_detail, name='streaming_detail'),
    path('', views.streaming_movie_list, name='streaming_movie_list'),  # 영화 목록 페이지
    path('movie/<str:movie_id>/', views.streaming_movie_detail, name='streaming_movie_detail'),  # 영화 상세 페이지
    path('api/movies/', views.movie_list, name='movie_list'),
    path('api/movies/<str:movie_id>/', views.movie_detail, name='movie_detail'),
    path('poster/<str:poster_id>/', views.get_streaming_movie_poster_image, name='streaming_movie_poster'),
]