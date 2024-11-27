from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import ProfileUpdateForm
from django.core.paginator import Paginator
from streaming.models import StreamingMovie
from funding.models import FundingMovie
from pymongo import MongoClient
from mongodbconnect.settings import client
from django.contrib.auth.models import User

# MongoDB 클라이언트 및 데이터베이스 설정
db = client['mongodatabase']
collection = db['funding_fundingmovie']

def ensure_django_user(request_user):
    """
    MongoDBUser 객체를 Django User 객체로 변환.
    """
    if not isinstance(request_user, User):  # MongoDBUser일 경우 변환
        try:
            django_user, created = User.objects.get_or_create(
                username=request_user.username,
                defaults={'email': getattr(request_user, 'email', '')}
            )
            return django_user
        except Exception as e:
            print(f"Error ensuring Django User: {e}")
            return None
    return request_user


@login_required
def my_projects(request):
    """
    내가 등록한 프로젝트 보기.
    """
    user = ensure_django_user(request.user)
    if user is None:
        return redirect('signin')  # 유효한 사용자 객체가 없으면 로그인 페이지로 리디렉션

    # MongoDB에서 현재 사용자가 등록한 프로젝트 검색
    user_projects = list(collection.find({"creator_id": str(user.id)}))

    return render(request, 'mypage/my_projects.html', {'user_projects': user_projects})


@login_required
def funded_movies(request):
    """
    사용자가 후원한 영화 목록 보기.
    """
    user = ensure_django_user(request.user)
    if user is None:
        return redirect('signin')

    # MongoDB에서 현재 사용자가 후원한 영화 검색
    funded_movies = list(collection.find({"backers": {"$elemMatch": {"user_id": str(user.id)}}}))

    return render(request, 'mypage/funded_movies.html', {'funded_movies': funded_movies})


@login_required
def purchased_movies(request):
    """
    사용자가 구매한 영화 목록을 가져오고 페이징 처리.
    """
    user = ensure_django_user(request.user)
    if user is None:
        return redirect('signin')

    # 로그인한 사용자가 구매한 영화 목록 필터링
    purchased_movies = StreamingMovie.objects.filter(viewers=user).only('title', 'genre', 'time')

    # Paginator 적용: 페이지당 10개 영화
    paginator = Paginator(purchased_movies, 10)
    page_number = request.GET.get('page')  # 현재 페이지 번호
    page_movies = paginator.get_page(page_number)  # 해당 페이지의 영화들 가져오기

    return render(request, 'mypage/purchased_movies.html', {'movies': page_movies})


@login_required
def mypage(request):
    """
    마이페이지 메인 화면.
    """
    user = ensure_django_user(request.user)
    if user is None:
        return redirect('signin')

    # 구매한 영화 데이터
    purchased_movies = StreamingMovie.objects.filter(viewers=user).only('title', 'genre', 'time')

    return render(request, 'mypage/mypage.html', {'user': user, 'movies': purchased_movies})


@login_required
def update_profile(request):
    """
    사용자 프로필 수정 기능.
    """
    user = ensure_django_user(request.user)
    if user is None:
        return redirect('signin')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage:mypage')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'mypage/update_profile.html', {'form': form})


@login_required
def change_password(request):
    """
    사용자 비밀번호 변경 기능.
    """
    user = ensure_django_user(request.user)
    if user is None:
        return redirect('signin')

    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 세션 유지
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('mypage:mypage')
        else:
            messages.error(request, '비밀번호 변경에 실패했습니다.')
    else:
        form = PasswordChangeForm(user=user)

    return render(request, 'mypage/change_password.html', {'form': form})
