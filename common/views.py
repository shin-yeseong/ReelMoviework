from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
#from .models import User, ContactInfo, RegistrationInfo, SecurityInfo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from bson.objectid import ObjectId
from datetime import datetime

# 사용자 회원가입 뷰
from django.shortcuts import render, redirect
#from .models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime

from django.shortcuts import render, redirect
#from .models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime

from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId
from datetime import datetime
import re
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.conf import settings
from pymongo import MongoClient
from django.utils.timezone import now

import uuid
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.http import HttpResponse
from django.urls import reverse
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from bson.objectid import ObjectId
from django.utils.crypto import get_random_string
from pymongo import MongoClient
from django.http import JsonResponse

app_name = 'common'

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://jklas187:PI9IWptT59WMOYZF@likemovie.toohv.mongodb.net/?retryWrites=true&w=majority')
db = client['mongodatabase']
users_collection = db['user']

# MongoDB 임시 저장소 설정
temporary_users_collection = db['temporary_users']

# 회원가입 뷰
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth_str = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        role = request.POST.get('role', 'viewer')
        bank = request.POST.get('bank')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        # 비밀번호 길이 확인
        if len(password) < 8:
            return render(request, 'signup.html', {'error': 'Password must be at least 8 characters long.'})

        hashed_password = make_password(password)

        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
            except ValueError:
                return render(request, 'signup.html', {'error': 'Invalid date format. Please use YYYY-MM-DD.'})

        if not email.endswith('@dgu.ac.kr'):
            return render(request, 'signup.html', {'error': 'Only @dgu.ac.kr emails are allowed.'})

        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return render(request, 'signup.html', {'error': 'Username already exists'})

        existing_email = users_collection.find_one({'email': email})
        if existing_email:
            return render(request, 'signup.html', {'error': 'Email already exists. Please use a different email.'})

        # 계정 활성화를 위한 인증 토큰 생성
        token = str(uuid.uuid4())

        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'role': role,
            'bank': bank,
            'phone_number': phone_number,
            'address': address,
            'is_active': False,  # 계정 비활성화 상태
            'token': token,
        }

        # 임시 컬렉션에 저장
        temporary_users_collection.insert_one(user_data)

        # 이메일로 인증 링크 전송
        verification_link = f"http://127.0.0.1:8000{reverse('verify_email', args=[token])}"
        subject = 'Please verify your email'
        message = f"Click the link to verify your email: {verification_link}"
        send_mail(subject, message, 'from@example.com', [email])

        return HttpResponse("A verification link has been sent to your email.")
    return render(request, 'signup.html')



sessions_collection = db['sessions']

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = users_collection.find_one({'username': username})

        if user:
            stored_password = user.get('password')

            if check_password(password, stored_password):
                users_collection.update_one(
                    {'username': username},
                    {'$set': {'last_login': datetime.now()}}
                )

                session_data = {
                    "user_id": str(user['_id']),
                    "user_role": user['role'],
                    "last_login": datetime.now().isoformat(),
                    "csrf_token": get_random_string(32),
                    "expiry": (datetime.now() + timedelta(weeks=2)).isoformat()
                }

                session_id = get_random_string(32)
                sessions_collection.insert_one({"_id": session_id, **session_data})
                print(f"Session data saved to MongoDB: {session_data}")

                request.session['session_id'] = session_id
                request.session['user_id'] = str(user['_id'])
                request.session.save()  # 세션 강제 저장
                print(f"Session ID set: {request.session.get('session_id')}")

                print(f"Authenticated user: {user}")  # 디버깅

                return redirect(request.GET.get('next', 'dashboard'))
            else:
                return render(request, 'signin.html', {'error': "Invalid password"})
        else:
            return render(request, 'signin.html', {'error': "User not found"})

    return render(request, 'signin.html')

def login_success(request):
    session_id = request.session.get('session_id')
    if not session_id:
        return JsonResponse({"message": "Not logged in"}, status=401)

    # MongoDB에서 세션 정보 확인
    session = sessions_collection.find_one({"_id": session_id})
    if not session:
        return JsonResponse({"message": "Session expired or not found"}, status=401)

    # 세션 만료 확인
    if datetime.fromisoformat(session['expiry']) < datetime.now():
        sessions_collection.delete_one({"_id": session_id})
        return JsonResponse({"message": "Session expired"}, status=401)

    # 사용자 정보 조회
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    if not user:
        return JsonResponse({"message": "User not found"}, status=404)

    # 사용자 정보를 템플릿으로 전달
    context = {
        "username": user.get("username"),
        "email": user.get("email"),
        "role": user.get("role"),
    }
    return render(request, "login.html", context)

# 이메일 인증 뷰
def verify_email(request, token):
    try:
        # 임시 컬렉션에서 사용자 검색
        user = temporary_users_collection.find_one({'token': token})
        if user:
            # 사용자 데이터 복사
            user_data = {key: user[key] for key in user if key != '_id'}
            user_data['is_active'] = True  # 계정 활성화
            user_data['date_joined'] = datetime.now()  # 가입 날짜 추가
            user_data.pop('token', None)  # 토큰 제거

            # 본 컬렉션에 저장
            users_collection.insert_one(user_data)

            # 임시 컬렉션에서 사용자 제거
            temporary_users_collection.delete_one({'_id': user['_id']})

            return HttpResponse("Your email has been verified! You can now log in.")
        else:
            return HttpResponse("Invalid or expired token.", status=400)
    except Exception as e:
        # 예외 처리
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

from django.contrib.auth.decorators import login_required
from django.contrib import messages  # 메시지 프레임워크 사용
from django.shortcuts import redirect

def logout_view(request):
    # 세션 ID 가져오기
    session_id = request.session.get('session_id')
    if not session_id:
        print("No session ID found for logout.")
        return redirect('signin')

    # MongoDB에서 현재 세션 ID로 세션 정보 조회
    session = sessions_collection.find_one({"_id": session_id})
    if not session:
        print(f"Session ID {session_id} not found in MongoDB.")
        return JsonResponse({"message": "Session not found"}, status=404)

    # 현재 사용자 ID 가져오기
    user_id = session.get("user_id")
    if not user_id:
        print("No user ID found in session.")
        return JsonResponse({"message": "User ID not found in session"}, status=404)

    # MongoDB에서 해당 사용자 ID의 모든 세션 삭제
    result = sessions_collection.delete_many({"user_id": user_id})
    print(f"Deleted {result.deleted_count} sessions for user_id: {user_id}")

    # 클라이언트 세션 삭제
    request.session.flush()
    print(f"All sessions for user_id {user_id} deleted and client session flushed.")
    return redirect('signin')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse



@login_required(login_url='signin')
def dashboard(request):
    return redirect('home')



