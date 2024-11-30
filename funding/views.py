# funding/views.py
from logging import exception
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, time
from mongodbconnect.settings import client
from .models import FundingMovie
from .forms import FundingMovieForm
import uuid
from datetime import datetime
from mongodbconnect import settings
from pymongo import MongoClient
import gridfs
from django.http import HttpResponse
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging
from django.views.decorators.csrf import csrf_exempt

# MongoDB 클라이언트 및 GridFS 설정
# MongoDB 클라이언트 및 데이터베이스 설정
client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client_mongo['mongodatabase']  # 데이터베이스 선택
collection = db['funding_fundingmovie']  # 컬렉션 선택
funding_upload_user_collection = db["funding_upload_user"]
sessions_collection = db["sessions"]
users_collection = db["user"]
funding_order_collection = db['funding_order']

# MongoDB 클라이언트 및 GridFS 설정
movie_fs = gridfs.GridFS(db)  # 동영상 파일용 GridFS
poster_fs = gridfs.GridFS(db)  # 포스터 이미지용 GridFS

@login_required(login_url='signin')
def upload_funding_movie(request):
    # 세션 ID 확인
    # session_id = request.session.get('session_id')
    # if not session_id:
    #     # return redirect('common:signin') # 로그인 페이지로 리다이렉트
    #     return render(request, 'error.html', {
    #         'alert_message': 'You do not have permission to upload funding movies.',
    #         'redirect_url': '/funding-page/'  # 올바른 경로로 변경
    #     })
    #
    # # MongoDB에서 세션 확인
    # session = sessions_collection.find_one({"_id": session_id})
    # if not session:
    #     return render(request, 'error.html', {
    #         'alert_message': 'You do not have permission to upload funding movies.',
    #         'redirect_url': '/funding-page/'  # 올바른 경로로 변경
    #     })
    #
    # # 사용자 정보 가져오기
    # user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    # if not user:
    #     return render(request, 'error.html', {
    #         'alert_message': 'You do not have permission to upload funding movies.',
    #         'redirect_url': '/funding-page/'  # 올바른 경로로 변경
    #     })
    #
    # # 사용자 역할 확인
    # if user.get('role') != 'host':
    #     return render(request, 'error.html', {
    #         'alert_message': 'You do not have permission to upload funding movies.',
    #         'redirect_url': '/funding-page/'  # 올바른 경로로 변경
    #     })

    user_role = request.user.role
    username = request.user.username

    if user_role != 'host':
        return render(request, 'permission_denied.html')

    if request.method == 'POST':
        print(request.POST.getlist('genre'))  # POST 요청에서 genre 값이 어떻게 전달되는지 확인

        # POST 데이터를 복사하고 genre 필드만 빈 값 없이 설정
        data = request.POST.copy()
        data.setlist('genre', [choice for choice in request.POST.getlist('genre') if choice])

        # Handling actors: Combine all actor inputs into a JSON-compatible list
        actors = data.getlist('actors')  # Assuming each actor is input separately
        data['actors'] = json.dumps(actors)  # Convert list to JSON string for form validation

        form = FundingMovieForm(data, request.FILES)
        print("POST 요청 수신")
        if form.is_valid():
            print("폼 유효성 검사 통과")

            # 'funding_deadline'을 datetime 객체로 변환
            funding_deadline = form.cleaned_data['funding_deadline']
            funding_deadline_datetime = datetime.combine(funding_deadline, time.min)

            # 현재 날짜와 시간을 create_date로 설정
            create_date_datetime = datetime.now()

            # Convert actors input to a JSON list format
            actors_input = request.POST.getlist('actors')

            try:
                # Convert the comma-separated list into a JSON-compatible list
                data['actors'] = json.dumps(actors_input)
            except (TypeError, json.JSONDecodeError):
                return render(request, 'upload_funding.html', {
                    'form': FundingMovieForm(data, request.FILES),
                    'error': 'Invalid actors format. Please enter a list of names.'
                })

            # Gather funding options
            funding_options = []
            for amount, benefit in zip(data.getlist('funding_amount'), data.getlist('funding_benefit')):
                funding_options.append({'amount': int(amount), 'benefit': benefit})

            funding_data = {
                "f_id": str(uuid.uuid4()),  # 고유 ID 생성
                "title": form.cleaned_data['title'],
                "genre": form.cleaned_data['genre'],
                "time": form.cleaned_data['time'],
                "intention": form.cleaned_data['intention'],
                "summary": form.cleaned_data['summary'],
                "making_description": form.cleaned_data['making_description'],
                "creator": form.cleaned_data['creator'],
                "actors": json.loads(data['actors']),  # Convert back to Python list for MongoDB
                "creator_talk": form.cleaned_data['creator_talk'],  # director's message
                "creator_id": str(request.user.id),  # 로그인한 사용자의 ID 저장
                "target_funding": form.cleaned_data['target_funding'],
                "funding_description": form.cleaned_data['funding_description'],
                "funding_deadline": funding_deadline_datetime,
                "create_date": create_date_datetime,
                "status": "funding",
                "backers": [],
                "backers_funding": [],
                "total_funding_amount": 0,
                "payment_history": [],
                "funding_options":funding_options
            }

            funding_amounts = request.POST.getlist('funding_amount')
            funding_benefits = request.POST.getlist('funding_benefit')
            funding_options = [{"amount": amt, "benefit": ben} for amt, ben in zip(funding_amounts, funding_benefits)]
            funding_data["funding_options"] = funding_options

            # GridFS에 파일 저장
            movie_file = request.FILES.get('movie_file')
            if movie_file:
                try:
                    file_id = movie_fs.put(movie_file, filename=movie_file.name)  # GridFS에 파일 저장
                    funding_data['movie_file_id'] = file_id  # 파일 ID를 데이터에 추가
                    print("파일이 GridFS에 저장되었습니다.")
                except Exception as e:
                    print("GridFS 파일 저장 중 오류 발생:", e)
                    return render(request, 'upload_funding.html', {'form': form, 'error': '파일 저장 중 오류가 발생했습니다.'})

            # GridFS에 포스터 이미지 파일 저장
            poster_image = request.FILES.get('poster_file')
            if poster_image:
                try:
                    poster_id = poster_fs.put(poster_image, filename=poster_image.name)  # GridFS에 이미지 파일 저장
                    funding_data['poster_image_id'] = poster_id  # 이미지 파일 ID 추가
                    print("포스터 이미지 파일이 GridFS에 저장되었습니다.")
                except Exception as e:
                    print("GridFS 이미지 파일 저장 중 오류 발생:", e)
                    return render(request, 'upload_funding.html',
                                  {'form': form, 'error': '이미지 파일 저장 중 오류가 발생했습니다.'})
            # MongoDB에 데이터 저장
            try:
                funding_id = collection.insert_one(funding_data).inserted_id
                print("MongoDB 저장 완료")

                # 로그 저장 추가_1125
                try:
                    funding_upload_log = {
                        "username": username,
                        "uploaded_funding_id": str(funding_id),
                        "title": funding_data["title"],
                        "upload_date": datetime.now(),
                    }
                    funding_upload_user_collection.insert_one(funding_upload_log)
                    print("업로드 로그 저장 완료")
                except Exception as log_error:
                    print("업로드 로그 저장 중 오류:", log_error)
                    return render(
                        request,
                        "upload_funding.html",
                        {"form": form, "error": "로그 저장 중 오류가 발생했습니다."},
                    )

                return redirect("funding:upload_success")
            except Exception as e:
                print("MongoDB 데이터 저장 중 오류 발생:", e)
                return render(
                    request,
                    "upload_success.html",
                    {"form": form, "error": "데이터 저장 중 오류가 발생했습니다."},
                )
        else:
            print("폼 유효성 검사 실패:", form.errors)
    else:
        form = FundingMovieForm()
    return render(request, "upload_funding.html", {"form": form})

def movie_list(request):
    movies = list(collection.find()) # DB에서 모든 영화 데이터 가져오기
    return render(request, 'movie_list.html', {'movies':movies})

def funding_detail(request, movie_id):
    movie = collection.find_one({"f_id":movie_id})
    if not movie:
        return HttpResponse(status=404)
    return render(request, 'movie_detail.html', {'movie':movie})

def funding_page(request):
    return render(request, 'funding_page.html')


def get_poster_image(request, poster_id):
    try:
        # ObjectId로 변환하여 파일 가져오기
        poster_object_id = ObjectId(poster_id)
        file = poster_fs.get(poster_object_id)

        # 파일 형식에 따라 Content-Type 동적으로 설정
        content_type = "image/jpeg"  # 기본값
        if file.filename.endswith('.png'):
            content_type = "image/png"
        elif file.filename.endswith('.gif'):
            content_type = "image/gif"

        image_data = file.read()
        return HttpResponse(image_data, content_type=content_type)
    except gridfs.errors.NoFile:
        return HttpResponse(status=404)  # 파일이 없으면 404 반환

def funding_payment_success(request):
    print("payment_success")

    movie_id = request.GET.get("movie_id")  # Extract movie_id from query parameters
    title = request.GET.get("title")  # Extract title from query parameters
    amount = request.GET.get("amount")  # Extract title from query parameters
    benefit = request.GET.get("benefit")  # Extract title from query parameters
    order_id = request.GET.get("orderId")
    user_id = request.user.id  # Logged-in user's ID
    user_name = request.user.username  # Logged-in user's username

    if not movie_id or not title:
        return JsonResponse({"error": "Missing movie_id or title"}, status=400)

    print(f"movie_id: {movie_id}, title: {title}")

    # Save the payment details to MongoDB
    funding_order = {
        "order_id": str(uuid.uuid4()),
        "user_id": user_id,
        "movie_id": movie_id,
        "movie_title": title,
        "payment_type": "forever",
        "amount": amount,
        "order_name": benefit,
        "order_date": datetime.now(),
        "status": "success",
    }
    funding_order_collection.insert_one(funding_order)

    # Update backers, backers_funding, and total_funding_amount
    try:
        collection.update_one(
            {"f_id": movie_id},
            {
                "$push": {
                    "backers": user_name,  # Add the user's name to backers
                    "backers_funding": {"user_id": user_id, "amount": int(amount)},  # Store funding details
                },
                "$inc": {"total_funding_amount": int(amount)},  # Increment the total funding amount
            },
        )
        print("Funding details updated successfully.")
    except Exception as e:
        print("Error updating funding details:", e)
        return JsonResponse({"error": "Failed to update funding details"}, status=500)

    # 결제 완료 처리
    return render(request, 'funding_payment_success.html', {
        'movie_id': movie_id,
        'title': title,
        'amount': amount,
        'benefit': benefit,
        'order_id': order_id,
    })

@csrf_exempt
def funding_payment_fail(request):
    title = request.GET.get("movie_title")
    amount = request.GET.get("amount")
    benefit = request.GET.get("benefit")
    return render(request, "funding_payment_fail.html", {
        "error_message": "결제가 실패했습니다. 다시 시도해 주세요.",
        "movie_title": title,
        "order_name": benefit,
        "amount": amount
    })

logger = logging.getLogger(__name__)

@login_required(login_url="signin")  # 로그인하지 않은 사용자는 signin 페이지로 리디렉션
def check_payment_status(request, movie_id, order_name):
    """
    결제 상태를 확인하는 뷰 함수
    :param order_name:
    :param request: Django WSGIRequest 객체
    :param movie_id: 영화의 ID
    :return: JsonResponse
    """
    logger.info(f"check_payment_status 호출 - movie_id: {movie_id}, user_id: {request.user.id}")

    # 1. movie_id가 전달되지 않았을 경우 처리
    if not movie_id:
        logger.error("movie_id가 전달되지 않았습니다.")
        return JsonResponse({"error": "Invalid or missing movie_id"}, status=400)

    # 2. 현재 사용자의 ID 가져오기
    user_id = str(request.user.id)  # MongoDB에서는 문자열 ID를 사용

    # 3. MongoDB에서 결제 정보를 검색
    payment_record = funding_order_collection.find_one({"user_id": user_id, "movie_id": movie_id, "order_name": order_name})

    # 4. 결제 정보가 있을 경우
    if payment_record:
        logger.info(f"결제 완료 - user_id: {user_id}, movie_id: {movie_id}, order_name: {order_name}")
        return JsonResponse({"already_paid": True})  # 결제 완료 상태 반환
    else:
        logger.info(f"결제 필요 - user_id: {user_id}, movie_id: {movie_id}, order_name: {order_name}")
        return JsonResponse({"already_paid": False})  # 결제 필요 상태 반환