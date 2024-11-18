from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import ProfileUpdateForm


@login_required
def mypage(request):
    """
    로그인한 사용자의 정보를 보여주는 뷰.
    """
    user = request.user
    return render(request, 'mypage/mypage.html', {'user': user})

@login_required
def update_profile(request):
    """
    사용자 프로필 수정 기능.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            # 사용자 정보를 업데이트
            request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
            request.user.last_name = form.cleaned_data.get('last_name', request.user.last_name)
            request.user.email = form.cleaned_data.get('email', request.user.email)
            request.user.date_of_birth = form.cleaned_data.get('date_of_birth', request.user.date_of_birth)
            request.user.gender = form.cleaned_data.get('gender', request.user.gender)
            request.user.bank = form.cleaned_data.get('bank', request.user.bank)
            request.user.phone_number = form.cleaned_data.get('phone_number', request.user.phone_number)
            request.user.address = form.cleaned_data.get('address', request.user.address)
            request.user.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage:mypage')
    else:
        # 초기 데이터 설정
        form = ProfileUpdateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'date_of_birth': request.user.date_of_birth,
            'gender': request.user.gender,
            'bank': request.user.bank,
            'phone_number': request.user.phone_number,
            'address': request.user.address,
        })

    return render(request, 'mypage/update_profile.html', {'form': form})


@login_required
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
