from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('funded-movies/', views.funded_movies, name='funded_movies'),
    path('my-projects/', views.my_projects, name='my_projects'),  # 내가 등록한 프로젝트
]
