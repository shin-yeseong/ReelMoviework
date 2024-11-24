# main_page/views.py
from django.shortcuts import render

# 메인 페이지 뷰
def home(request):
    return render(request, 'home.html')

# 펀딩 영화 페이지 뷰
def funding_movie_page(request):
    return render(request, 'funding_page.html')

# 스트리밍 영화 페이지 뷰
def streaming_movie_page(request):
    return render(request, 'streaming_page.html')

def signup_page(request):
    return render(request, 'signup.html')

def login_page(request):
    return render(request, 'signin.html')




