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
from common.middleware import MongoDBUser

# MongoDB 클라이언트 및 데이터베이스 설정


from pymongo import MongoClient, errors

try:
    client = MongoClient(
        'mongodb+srv://jklas187:PI9IWptT59WMOYZF@likemovie.toohv.mongodb.net/?retryWrites=true&w=majority',
        serverSelectionTimeoutMS=15000,  # 타임아웃 설정
        socketTimeoutMS=15000
    )
    db = client['mongodatabase']
    users_collection = db['user']
    collection = db['funding_fundingmovie']
    # 연결 테스트
    client.admin.command('ping')
    print("[DEBUG] MongoDB 연결 성공")
except errors.ServerSelectionTimeoutError as e:
    print(f"[DEBUG] MongoDB 서버 연결 실패: {e}")
    users_collection = None

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


from bson import ObjectId
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password, check_password
from .forms import ProfileUpdateForm, PasswordChangeForm

from bson import ObjectId

@login_required
def update_profile(request):
    user = request.user  # Middleware에서 설정한 MongoDBUser 객체
    if not isinstance(user, MongoDBUser):
        messages.error(request, '로그인 정보가 잘못되었습니다.')
        return redirect('signin')

    if request.method == 'POST':
        bank = request.POST.get('bank', '').strip()
        address = request.POST.get('address', '').strip()

        try:
            # MongoDB 업데이트
            result = users_collection.update_one(
                {'_id': ObjectId(user.id)},
                {'$set': {'bank': bank, 'address': address}}
            )
            if result.modified_count > 0:
                messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            else:
                messages.warning(request, '변경된 내용이 없습니다.')

        except Exception as e:
            print(f"[DEBUG] MongoDB 업데이트 오류: {e}")
            messages.error(request, '프로필 업데이트 중 문제가 발생했습니다.')

    return render(request, 'mypage/update_profile.html', {
        'bank': user.bank,
        'address': user.address,
    })

from django.contrib.auth.hashers import make_password

from django.contrib.auth.hashers import make_password

from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def change_password(request):
    """
    사용자 비밀번호 변경
    """
    user = request.user  # Middleware에서 설정된 MongoDBUser 객체 사용
    if not isinstance(user, MongoDBUser):
        messages.error(request, '로그인 정보가 잘못되었습니다.')
        return redirect('signin')

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # 기존 비밀번호 검증
        if not user.check_password(old_password):
            messages.error(request, '기존 비밀번호가 올바르지 않습니다.')
            return render(request, 'mypage/change_password.html')

        # 새 비밀번호와 확인 비밀번호 일치 여부 확인
        if new_password != confirm_password:
            messages.error(request, '새 비밀번호와 확인 비밀번호가 일치하지 않습니다.')
            return render(request, 'mypage/change_password.html')

        # 새 비밀번호 검증 (예: 최소 길이, 복잡성 등)
        if len(new_password) < 8:
            messages.error(request, '비밀번호는 최소 8자 이상이어야 합니다.')
            return render(request, 'mypage/change_password.html')

        try:
            # 비밀번호 해싱 후 업데이트
            hashed_password = make_password(new_password)
            result = users_collection.update_one(
                {'_id': ObjectId(user.id)},
                {'$set': {'password': hashed_password}}
            )
            if result.modified_count > 0:
                messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            else:
                messages.warning(request, '비밀번호 변경에 실패했습니다.')

        except Exception as e:
            print(f"[DEBUG] 비밀번호 업데이트 오류: {e}")
            messages.error(request, '비밀번호 변경 중 문제가 발생했습니다.')

        return redirect('mypage:mypage')

    return render(request, 'mypage/change_password.html')
