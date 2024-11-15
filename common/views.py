from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from .models import User, ContactInfo, RegistrationInfo, SecurityInfo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail


# 사용자 회원가입 뷰
from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime

from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # 빈 문자열인 경우 None으로 변환, 날짜는 datetime.date로 변환
        date_of_birth_str = request.POST.get('date_of_birth')
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                return render(request, 'signup.html', {'error': 'Invalid date format. Please use YYYY-MM-DD.'})

        gender = request.POST.get('gender')
        role = request.POST.get('role', 'viewer')
        bank = request.POST.get('bank') or None

        # 새로운 사용자 객체 생성
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            role=role,
            bank=bank
        )

        try:
            # MongoDB 호환성 문제로 insert_one 사용
            user.save() # 메서드를 사용해보세요
            return redirect('signin')
        except Exception as e:
            # 예외 처리
            return render(request, 'signup.html', {'error': str(e)})

    return render(request, 'signup.html')




# 로그인 뷰
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            return redirect('profile')  # 로그인 후 리디렉션할 페이지
        else:
            return HttpResponse("Invalid login credentials")

    return render(request, 'signin.html')


# 사용자 정보 페이지 (사용자 정보 확인)
@login_required

def profile(request):
    # 현재 로그인된 사용자
    user = request.user

    # 각 관련 정보를 가져옵니다.
    contact_info = ContactInfo.objects.get(user=user)
    registration_info = RegistrationInfo.objects.get(user=user)
    security_info = SecurityInfo.objects.get(user=user)

    # 템플릿으로 데이터 전달
    return render(request, 'profile.html', {
        'user': user,
        'contact_info': contact_info,
        'registration_info': registration_info,
        'security_info': security_info
    })


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


# 비밀번호 재설정
def reset_password(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        user.set_password(new_password)
        user.save()
        return redirect('main_signin')
    return render(request, 'reset_password.html', {'user': user})


# 사용자 계정 삭제 (탈퇴)
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('main_signup')
    return render(request, 'delete_account.html')
