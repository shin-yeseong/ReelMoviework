from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import ProfileUpdateForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from streaming.models import StreamingMovie  # Streaming 앱의 모델 import
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from funding.models import FundingMovie
from pymongo import MongoClient
from mongodbconnect.settings import client

# MongoDB 클라이언트 및 데이터베이스 설정
db = client['mongodatabase']
collection = db['funding_fundingmovie']


# 내가 등록한 프로젝트 보기
def my_projects(request):
    user = request.user if request.user.is_authenticated else None

    # 로그인된 사용자가 없을 경우 빈 리스트 반환
    if not user:
        user_projects = []
    else:
        # MongoDB에서 현재 사용자가 등록한 프로젝트 검색
        db = client['mongodatabase']
        collection = db['funding_fundingmovie']
        user_projects = list(collection.find({"creator_id": str(user.id)}))

    return render(request, 'mypage/my_projects.html', {'user_projects': user_projects})
def funded_movies(request):
    user = request.user if request.user.is_authenticated else None

    # 로그인된 사용자가 없을 경우 빈 리스트 반환
    if not user:
        funded_movies = []
    else:
        # MongoDB에서 현재 사용자가 후원한 영화 검색
        db = client['mongodatabase']
        collection = db['funding_fundingmovie']
        funded_movies = list(collection.find({"backers": {"$elemMatch": {"user_id": str(user.id)}}}))

    return render(request, 'mypage/funded_movies.html', {'funded_movies': funded_movies})
def purchased_movies(request):
    """
    사용자가 구매한 영화 목록을 가져오고 페이징 처리.
    """
    user = request.user

    # 로그인한 사용자가 구매한 영화 목록 필터링
    purchased_movies = StreamingMovie.objects.filter(viewers=user).only('title', 'genre', 'time')

    # Paginator 적용: 페이지당 10개 영화
    paginator = Paginator(purchased_movies, 10)
    page_number = request.GET.get('page')  # 현재 페이지 번호
    page_movies = paginator.get_page(page_number)  # 해당 페이지의 영화들 가져오기

    # 템플릿에 페이지 객체 전달
    return render(request, 'mypage/purchased_movies.html', {'movies': page_movies})


from django.shortcuts import render
from streaming.models import StreamingMovie  # Streaming 앱의 모델 import

def mypage(request):
    """
    로그인 없이도 mypage 화면 확인 가능.
    """
    # 기본 더미 데이터 설정
    class DummyUser:
        username = "TestUser"
        email = "test@example.com"
        first_name = "Test"
        last_name = "User"
        date_of_birth = "2000-01-01"
        gender = "M"
        phone_number = "010-1234-5678"
        address = "123 Test Street"

    user = DummyUser()

    # 기본 더미 영화 데이터
    purchased_movies = [
        {"title": "Demo Movie 1", "genre": ["Action", "Comedy"], "time": 120},
        {"title": "Demo Movie 2", "genre": ["Drama"], "time": 90},
    ]

    return render(request, 'mypage/mypage.html', {'user': user, 'movies': purchased_movies})


def update_profile(request):
    """
    사용자 프로필 수정 기능.
    """
    # 로그인 없이 더미 데이터로 테스트
    class DummyUser:
        first_name = "Test"
        last_name = "User"
        email = "test@example.com"
        date_of_birth = "2000-01-01"
        gender = "M"
        bank = "Test Bank"
        phone_number = "010-1234-5678"
        address = "123 Test Street"

    user = request.user if request.user.is_authenticated else DummyUser()

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            # 더미 데이터를 업데이트
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.email = form.cleaned_data.get('email', user.email)
            user.date_of_birth = form.cleaned_data.get('date_of_birth', user.date_of_birth)
            user.gender = form.cleaned_data.get('gender', user.gender)
            user.bank = form.cleaned_data.get('bank', user.bank)
            user.phone_number = form.cleaned_data.get('phone_number', user.phone_number)
            user.address = form.cleaned_data.get('address', user.address)
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage:mypage')
    else:
        # 초기 데이터 설정
        form = ProfileUpdateForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_of_birth': user.date_of_birth,
            'gender': user.gender,
            'bank': user.bank,
            'phone_number': user.phone_number,
            'address': user.address,
        })

    return render(request, 'mypage/update_profile.html', {'form': form})


def change_password(request):
    """
    사용자 비밀번호 변경 기능.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 세션 유지
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('mypage:mypage')
        else:
            messages.error(request, '비밀번호 변경에 실패했습니다.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'mypage/change_password.html', {'form': form})
