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

@login_required
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



@login_required
def mypage(request):
    """
    마이페이지 메인 화면: 내 정보와 구매한 영화 목록 표시
    """
    user = request.user
    purchased_movies = StreamingMovie.objects.filter(viewers=user).only('title', 'genre', 'time')

    return render(request, 'mypage/mypage.html', {
        'user': user,
        'movies': purchased_movies
    })
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
