# funding/urls.py
from django.urls import path
from . import views

app_name = 'funding'

urlpatterns = [
    path('upload/', views.upload_funding_movie, name='upload_funding_movie'),
    path('<int:movie_id>/', views.funding_detail, name='funding_detail'),
]
