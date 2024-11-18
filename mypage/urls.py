from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', views.mypage, name='mypage'),  # 마이페이지
    path('update/', views.update_profile, name='update_profile'),  # 프로필 수정
    path('change-password/', views.change_password, name='change_password'),  # 비밀번호 변경
]
