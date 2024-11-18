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

# MongoDB 연결 설정 (데이터베이스 이름과 컬렉션 이름 수정)
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

        # 비밀번호 해시 처리
        hashed_password = make_password(password)

        # 생년월일 변환
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
            except ValueError:
                return render(request, 'signup.html', {'error': 'Invalid date format. Please use YYYY-MM-DD.'})

        # 중복 사용자 확인
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return render(request, 'signup.html', {'error': 'Username already exists'})

        # 현재 시각으로 가입일 설정
        date_joined = datetime.now()

        # 사용자 ID 자동 생성 (MongoDB의 `_id` 사용 대신 직접 관리)
        user_id = users_collection.count_documents({}) + 1

        # MongoDB에 사용자 정보 저장
        user_data = {
            'user_id': user_id,
            'last_login': None,
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
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'date_joined': date_joined,
        }

        try:
            users_collection.insert_one(user_data)
            return redirect('signin')
        except Exception as e:
            return render(request, 'signup.html', {'error': str(e)})

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
                return redirect('home')
            else:
                return render(request, 'signin.html', {'error': "Invalid password"})
        else:
            return render(request, 'signin.html', {'error': "User not found"})

    return render(request, 'signin.html')


# 이메일 발송 기능
def send_email(request):
    if request.method == 'POST':
        recipient = request.POST.get('email')

        # 이메일 주소가 @dgu.ac.kr로 끝나는지 확인하는 조건
        if re.match(r'^[\w\.-]+@dgu\.ac\.kr$', recipient):
            subject = 'Welcome to our platform'
            message = 'Thank you for signing up. We are happy to have you.'
            send_mail(subject, message, 'from@example.com', [recipient])
            return HttpResponse("Email sent successfully!")
        else:
            return HttpResponse("Only @dgu.ac.kr email addresses are allowed.")

    return render(request, 'account/send_email.html')


# 이메일 발송 기능
import re
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render


'''def send_email(request):
    if request.method == 'POST':
        recipient = request.POST.get('email')

        # 이메일 주소가 @dgu.ac.kr로 끝나는지 확인하는 조건
        if re.match(r'^[\w\.-]+@dgu\.ac\.kr$', recipient):
            subject = 'Welcome to our platform'
            message = 'Thank you for signing up. We are happy to have you.'
            send_mail(subject, message, 'from@example.com', [recipient])
            return HttpResponse("Email sent successfully!")
        else:
            return HttpResponse("Only @dgu.ac.kr email addresses are allowed.")

    return render(request, 'account/send_email.html')'''


