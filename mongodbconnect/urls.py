"""
URL configuration for mongodbconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# mongodbconnect/urls.py
from django.contrib import admin
from django.urls import path, include

from common.views import signin, signup
from main_page.views import home, funding_movie_page, streaming_movie_page, login_page, signup_page \
    # 필요한 뷰 임포트
from django.urls import path
from mypage import views  # mypage 앱에서 views 모듈 임포트
from django.contrib import admin
from django.urls import path, include
from main_page.views import home, funding_movie_page, streaming_movie_page
from common.views import signin, signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('streaming/', include('streaming.urls')),
    path('funding/', include('funding.urls')),
    path('common/', include('common.urls')),  # common 앱의 URL 포함
    path('', home, name='home'),  # 메인 페이지 URL
    path('funding-page/', funding_movie_page, name='funding_movie_page'),  # 펀딩 영화 페이지 URL
    path('streaming-page/', streaming_movie_page, name='streaming_movie_page'),  # 스트리밍 영화 페이지 URL
    path('signup-page/', signup, name='signup_page'),  # 회원가입
    path('login-page/', signin, name='login_page'),  # 로그인
    path('mypage/', include('mypage.urls', namespace='mypage')),  # mypage 앱 연결
]