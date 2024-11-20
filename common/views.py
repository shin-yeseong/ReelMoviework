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
        date_joined = datetime.now()

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
            'is_active': False,  # 계정 비활성화 상태로 저장
            'token': token,
            'date_joined': date_joined,
        }

        users_collection.insert_one(user_data)

        # 이메일로 인증 링크 전송
        verification_link =  f"http://127.0.0.1:8000{reverse('verify_email', args=[token])}"
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
                return redirect('/')
            else:
                return render(request, 'signin.html', {'error': "Invalid password"})
        else:
            return render(request, 'signin.html', {'error': "User not found"})

    return render(request, 'signin.html')


def verify_email(request, token):
    try:
        # MongoDB에서 토큰을 가진 사용자 검색
        print(f"Token received: {token}")  # 디버깅용
        user = users_collection.find_one({'token': token})
        print(f"User found: {user}")  # 디버깅용

        if user:
            # 사용자 활성화 처리
            users_collection.update_one(
                {'token': token},
                {'$set': {'is_active': True, 'token': None}}
            )
            return HttpResponse("Your email has been verified! You can now log in.")
        else:
            return HttpResponse("Invalid or expired token.", status=400)
    except Exception as e:
        # 예외 처리
        return HttpResponse(f"An error occurred: {str(e)}", status=500)





