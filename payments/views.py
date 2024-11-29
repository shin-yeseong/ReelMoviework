import datetime
import uuid

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests, json, base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongodbconnect import settings
from pymongo import MongoClient

billing_key_map = {}

# MongoDB 클라이언트 및 데이터베이스 설정
client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client_mongo['mongodatabase']  # 데이터베이스 선택
collection = db['streaming_streamingmovie']  # 컬렉션 선택
streaming_orders_collection = db['streaming_order']


# API 요청에 헤더를 생성하는 함수
def create_headers(secret_key):
    # 토스페이먼츠 API는 시크릿 키를 사용자 ID로 사용하고, 비밀번호는 사용하지 않습니다.
    # 비밀번호가 없다는 것을 알리기 위해 시크릿 키 뒤에 콜론을 추가합니다.
    # @docs https://docs.tosspayments.com/reference/using-api/authorization#%EC%9D%B8%EC%A6%9D
    userpass = f"{secret_key}:"
    encoded_u = base64.b64encode(userpass.encode()).decode()
    return {
        "Authorization": f"Basic {encoded_u}",
        "Content-Type": "application/json"
    }


# API 요청을 호출하고 응답 핸들링하는 함수
def send_payment_request(url, params, headers):
    response = requests.post(url, json=params, headers=headers)
    return response.json(), response.status_code


# 성공 및 실패 페이지 렌더링하는 함수
def handle_response(request, resjson, status_code, success_template, fail_template):
    if status_code == 200:
        return render(request, success_template, {
            "res": json.dumps(resjson, indent=4),
            "respaymentKey": resjson.get("paymentKey"),
            "resorderId": resjson.get("orderId"),
            "restotalAmount": resjson.get("totalAmount")
        })
    else:
        return render(request, fail_template, {
            "code": resjson.get("code"),
            "message": resjson.get("message")
        })


# 페이지 렌더링 함수
def widgetCheckout(request):
    return render(request, './widget/checkout.html')


def brandpayCheckout(request):
    return render(request, './brandpay/checkout.html')


def paymentCheckout(request):
    return render(request, './payment/checkout.html')


def paymentBilling(request):
    return render(request, './payment/billing.html')


# 결제 성공 및 실패 핸들링
# TODO: 개발자센터에 로그인해서 내 시크릿 키를 입력하세요. 시크릿 키는 외부에 공개되면 안돼요.
# @docs https://docs.tosspayments.com/reference/using-api/api-keys
def widgetSuccess(request):
    return process_payment(request, "test_sk_DpexMgkW36RKKkgXJvgw3GbR5ozO", './widget/success.html')


def paymentSuccess(request):
    return process_payment(request, "test_sk_DpexMgkW36RKKkgXJvgw3GbR5ozO", './payment/success.html')


def brandpaySuccess(request):
    return process_payment(request, "test_sk_DpexMgkW36RKKkgXJvgw3GbR5ozO", './brandpay/success.html')


# 결제 승인 호출하는 함수
# @docs https://docs.tosspayments.com/guides/v2/payment-widget/integration#3-결제-승인하기
def process_payment(request, secret_key, success_template):
    orderId = request.GET.get('orderId')
    amount = request.GET.get('amount')
    paymentKey = request.GET.get('paymentKey')

    url = "https://api.tosspayments.com/v1/payments/confirm"
    headers = create_headers(secret_key)
    params = {
        "orderId": orderId,
        "amount": amount,
        "paymentKey": paymentKey
    }

    resjson, status_code = send_payment_request(url, params, headers)
    return handle_response(request, resjson, status_code, success_template, 'fail.html')


# Fail page rendering view
def fail(request):
    return render(request, "fail.html", {
        "code": request.GET.get('code'),
        "message": request.GET.get('message')
    })


# 빌링키 발급
# AuthKey 로 카드 빌링키 발급 API 를 호출하세요
# @docs https://docs.tosspayments.com/reference#authkey로-카드-빌링키-발급
@csrf_exempt
def issueBillingKey(request):
    try:
        data = json.loads(request.body)
        customerKey = data.get('customerKey')
        authKey = data.get('authKey')

        if not customerKey or not authKey:
            raise ValueError("Missing parameters")
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

    url = "https://api.tosspayments.com/v1/billing/authorizations/issue"
    secret_key = "test_sk_zXLkKEypNArWmo50nX3lmeaxYG5R"
    headers = create_headers(secret_key)
    params = {
        "customerKey": customerKey,
        "authKey": authKey
    }

    resjson, status_code = send_payment_request(url, params, headers)

    if status_code == 200:
        billing_key_map[customerKey] = resjson.get('billingKey')

    return JsonResponse(resjson, status=status_code)


# 자동결제 승인
@csrf_exempt
def confirm_billing(request):
    try:
        data = json.loads(request.body)
        customerKey = data.get('customerKey')
        amount = data.get('amount')
        orderId = data.get('orderId')
        orderName = data.get('orderName')
        customerEmail = data.get('customerEmail')
        customerName = data.get('customerName')

        if not all([customerKey, amount, orderId, orderName, customerEmail, customerName]):
            raise ValueError("Missing parameters")

        # 저장해두었던 빌링키로 카드 자동결제 승인 API 를 호출하세요.
        billingKey = billing_key_map.get(customerKey)
        if not billingKey:
            return JsonResponse({'error': 'Billing key not found'}, status=400)

    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

    url = f"https://api.tosspayments.com/v1/billing/{billingKey}"
    secret_key = "test_sk_zXLkKEypNArWmo50nX3lmeaxYG5R"
    headers = create_headers(secret_key)
    params = {
        "customerKey": customerKey,
        "amount": amount,
        "orderId": orderId,
        "orderName": orderName,
        "customerEmail": customerEmail,
        "customerName": customerName
    }

    resjson, status_code = send_payment_request(url, params, headers)

    if status_code == 200:
        return JsonResponse(resjson, status=status_code)
    else:
        return JsonResponse(resjson, status=status_code)


# 브랜드페이 Access Token 발급
def callback_auth(request):
    customerKey = request.GET.get('customerKey')
    code = request.GET.get('code')

    if not customerKey or not code:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    url = "https://api.tosspayments.com/v1/brandpay/authorizations/access-token"
    secret_key = "test_sk_aBX7zk2yd8yoXwoJ0gqVx9POLqKQ"
    headers = create_headers(secret_key)
    params = {
        "grantType": "AuthorizationCode",
        "customerKey": customerKey,
        "code": code
    }

    resjson, status_code = send_payment_request(url, params, headers)

    if status_code == 200:
        return JsonResponse(resjson, status=status_code)
    else:
        return JsonResponse(resjson, status=status_code)

@csrf_exempt
def streaming_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            movie_id = data.get('movie_id')
            movie_title = data.get('title')  # 추가: 영화 제목
            payment_type = "forever"  # 스트리밍은 영구 소장만 가능
            amount = 2000  # 결제 금액 (고정)

            # 주문 데이터 생성
            streaming_order = {
                "order_id": str(uuid.uuid4()),
                "user_id": user_id,
                "movie_id": movie_id,
                "movie_title": movie_title,  # 영화 제목 저장
                "payment_type": payment_type,
                "amount": amount,
                "order_date": datetime.now(),
                "status": "success"
            }

            # MongoDB에 저장
            streaming_orders_collection.insert_one(streaming_order)
            return JsonResponse({"message": "Streaming payment saved successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_streaming_payment_info(request, movie_id):
    try:
        # 영화 정보를 MongoDB에서 가져오기
        movie = db['streaming_order'].find_one({"_id": movie_id})  # Replace with your actual movie collection
        if not movie:
            return JsonResponse({"error": "Movie not found"}, status=404)

        # 반환할 데이터
        data = {
            "movie_id": str(movie["_id"]),
            "user_id": movie["user_id"],
            "title": movie["title"],
            "amount": 1000,  # 고정 금액
            "customer_email": request.user.email,
            "customer_name": request.user.get_full_name()
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required(login_url='signin')
def check_payment_status(request, movie_id):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({"error": "not_logged_in"}, status=401)

    payment_record = streaming_orders_collection.find_one({"user_id": user_id, "movie_id": movie_id})

    if payment_record:
        return JsonResponse({"can_watch": True})
    else:
        return JsonResponse({"can_watch": False})