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
    if isinstance(request_user, User):
        return request_user
    # MongoDB에서 사용자 데이터를 가져와 Django User로 변환
    try:
        django_user, created = User.objects.get_or_create(
            username=request_user.username,
            defaults={
                'email': request_user.email,
                'first_name': getattr(request_user, 'first_name', ''),
                'last_name': getattr(request_user, 'last_name', ''),
            }
        )
        if not created:
            django_user.email = request_user.email
            django_user.first_name = getattr(request_user, 'first_name', '')
            django_user.last_name = getattr(request_user, 'last_name', '')
            django_user.save()
        return django_user
    except Exception as e:
        print(f"Error in ensure_django_user: {e}")
        return None



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


# MongoDB 연결 설정
client = MongoClient(
    'your_mongo_connection_string',
    maxPoolSize=50,  # 최대 연결 풀 크기
    serverSelectionTimeoutMS=5000  # 연결 타임아웃 (ms)
)
db = client['mongodatabase']
users_collection = db['user']


@login_required
def mypage(request):
    user_id = request.session.get('user_id')
    print("세션에서 가져온 user_id:", user_id)

    if not user_id:
        return render(request, 'mypage/mypage.html', {'error': 'No user ID in session'})

    try:
        user_data = users_collection.find_one({"_id": user_id})  # ObjectId 제거
        if not user_data:
            print(f"사용자를 찾을 수 없습니다. user_id: {user_id}")
            return render(request, 'mypage/mypage.html', {'error': 'User not found in MongoDB'})

        # 데이터 변환
        if 'last_login' in user_data:
            user_data['last_login'] = user_data['last_login'].strftime('%Y-%m-%d %H:%M:%S')
        if 'date_joined' in user_data:
            user_data['date_joined'] = user_data['date_joined'].strftime('%Y-%m-%d %H:%M:%S')

        print("MongoDB에서 가져온 사용자 데이터:", user_data)
        return render(request, 'mypage/mypage.html', {'user': user_data})
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return render(request, 'mypage/mypage.html', {'error': 'An error occurred while fetching user data'})

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
            print(form.errors)  # 디버깅: 폼 오류 출력
            messages.error(request, '프로필 업데이트에 실패했습니다.')
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
            try:
                # 비밀번호 변경 및 저장
                user = form.save()

                # MongoDB에 비밀번호 동기화
                hashed_password = user.password  # 해싱된 비밀번호 가져오기
                users_collection.update_one(
                    {"username": user.username},
                    {"$set": {"password": hashed_password}}
                )

                # 세션 갱신
                update_session_auth_hash(request, user)

                messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
                return redirect('mypage:mypage')
            except Exception as e:
                print(f"MongoDB 저장 에러: {e}")
                messages.error(request, '비밀번호 변경 중 문제가 발생했습니다.')
        else:
            print("폼 오류:", form.errors)
            messages.error(request, '비밀번호 변경에 실패했습니다.')
    else:
        form = PasswordChangeForm(user=user)

    return render(request, 'mypage/change_password.html', {'form': form})
