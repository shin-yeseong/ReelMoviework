from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import ProfileUpdateForm
from common.models import User  # User 모델 import


def mypage(request):
    """
    로그인한 사용자의 정보를 보여주는 뷰.
    """
    user = request.user
    return render(request, 'mypage/mypage.html', {'user': user})


def update_profile(request):
    """
    사용자 프로필 수정 기능.
    """
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage:mypage')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)

    return render(request, 'mypage/update_profile.html', {'form': profile_form})


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
