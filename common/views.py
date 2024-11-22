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

import uuid
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.http import HttpResponse
from django.urls import reverse
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



# 로그인 뷰
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # MongoDB에서 사용자 조회
        user = users_collection.find_one({'username': username})

        if user:
            stored_password = user.get('password')

            # 비밀번호 확인
            if check_password(password, stored_password):
                # 마지막 로그인 시간 업데이트
                users_collection.update_one(
                    {'username': username},
                    {'$set': {'last_login': datetime.now()}}
                )
                request.session['user_id'] = str(user['_id'])
                request.session['user_role'] = user['role']

                return render(request, 'login.html')
            else:
                return render(request, 'signin.html', {'error': "Invalid password"})
        else:
            return render(request, 'signin.html', {'error': "User not found"})

    return render(request, 'signin.html')


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





