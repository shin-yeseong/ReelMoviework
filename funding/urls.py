# funding/urls.py
from django.urls import path
from . import views

app_name = 'funding'

urlpatterns = [
    path('upload/', views.upload_funding_movie, name='upload_funding_movie'),
    path('<str:movie_id>/', views.funding_detail, name='movie_detail'),
    path('movie/list/', views.movie_list, name='movie_list'),
    path('poster/<str:poster_id>/', views.get_poster_image, name="get_poster_image"),
    path('funding-page/', views.funding_page, name='funding_movie_page'),
]
