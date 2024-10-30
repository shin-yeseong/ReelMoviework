# streaming/urls.py
from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    path('<int:movie_id>/', views.streaming_detail, name='streaming_detail'),
]