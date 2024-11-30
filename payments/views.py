import datetime
import uuid

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import requests, json, base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongodbconnect import settings
from pymongo import MongoClient

billing_key_map = {}

# MongoDB 클라이언트 및 데이터베이스 설정
client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client_mongo['mongodatabase']  # 데이터베이스 선택
streaming_orders_collection = db['streaming_order']  # 스트리밍 주문 컬렉션
movies_collection = db['streaming_streamingmovie']  # 영화 데이터 컬렉션


# 스트리밍 결제 페이지
@login_required(login_url='/login/')
def payment_checkout(request):
    movie_title = request.GET.get('title', 'No Title')
    movie_id = request.GET.get('movie_id')

    context = {
        'movie_title': movie_title,
        'movie_id': movie_id,
        'amount': 1000,  # 고정 결제 금액
        'user_name': request.user.username,
        'user_email': request.user.email
    }
    return render(request, 'payment/checkout.html', context)


# 스트리밍 결제 API
@csrf_exempt
@login_required(login_url='/login/')
def streaming_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = str(request.user.id)  # 로그인된 사용자 ID
            movie_id = data.get('movie_id')
            movie_title = data.get('movie_title')  # 영화 제목
            amount = 1000  # 결제 금액 (고정)

            # 중복 결제 방지 확인
            existing_order = streaming_orders_collection.find_one({"user_id": user_id, "movie_id": movie_id})
            if existing_order:
                return JsonResponse({"message": "Payment already exists."}, status=400)

            # 결제 데이터 생성 및 저장
            streaming_order = {
                "order_id": str(uuid.uuid4()),
                "user_id": user_id,
                "movie_id": movie_id,
                "movie_title": movie_title,
                "amount": amount,
                "order_date": datetime.now(),
                "status": "success"
            }
            streaming_orders_collection.insert_one(streaming_order)

            return JsonResponse({"message": "Payment successful!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def check_payment_status(request, movie_id):
    try:
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({"error": "User ID is missing"}, status=400)

        # MongoDB에서 해당 영화와 사용자 ID에 대한 결제 기록 검색
        payment_record = streaming_orders_collection.find_one({"user_id": user_id, "movie_id": movie_id})

        if payment_record:
            return JsonResponse({"can_watch": True})  # 결제 기록이 있으면 영화 시청 가능
        else:
            return JsonResponse({"can_watch": False})  # 결제 기록이 없으면 영화 시청 불가
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 영화 보기 버튼 클릭 시
@login_required(login_url='/login/')
def play_or_pay(request, movie_id):
    user_id = str(request.user.id)

    # 결제 여부 확인
    payment_record = streaming_orders_collection.find_one({"user_id": user_id, "movie_id": movie_id})

    if payment_record:
        # 결제 완료된 경우
        return redirect(f'/streaming/movie/{movie_id}/')
    else:
        # 결제 필요
        movie = movies_collection.find_one({"_id": movie_id})
        if not movie:
            return JsonResponse({"error": "Movie not found"}, status=404)
        return redirect(f'/payments/payment/checkout?movie_id={movie_id}&title={movie["title"]}')


# 결제 성공 페이지 처리
def payment_success(request):
    return render(request, './payment/success.html')


# 결제 실패 페이지 처리
def payment_fail(request):
    return render(request, './payment/fail.html')