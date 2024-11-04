# funding/views.py
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

# MongoDB 클라이언트 및 GridFS 설정
# MongoDB 클라이언트 및 데이터베이스 설정
client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client_mongo['mongodatabase']  # 데이터베이스 선택
collection = db['funding_fundingmovie']  # 컬렉션 선택
fs = gridfs.GridFS(db)

# @login_required
def upload_funding_movie(request):
    if request.method == 'POST':
        print(request.POST.getlist('genre'))  # POST 요청에서 genre 값이 어떻게 전달되는지 확인

        # POST 데이터를 복사하고 genre 필드만 빈 값 없이 설정
        data = request.POST.copy()
        data.setlist('genre', [choice for choice in request.POST.getlist('genre') if choice])

        form = FundingMovieForm(data, request.FILES)
        print("POST 요청 수신")
        if form.is_valid():
            print("폼 유효성 검사 통과")

            # 'funding_deadline'을 datetime 객체로 변환
            funding_deadline = form.cleaned_data['funding_deadline']
            funding_deadline_datetime = datetime.combine(funding_deadline, time.min)

            # 현재 날짜와 시간을 create_date로 설정
            create_date_datetime = datetime.now()

            funding_data = {
                "f_id": str(uuid.uuid4()),  # 고유 ID 생성
                "title": form.cleaned_data['title'],
                "genre": form.cleaned_data['genre'],
                "time": form.cleaned_data['time'],
                "intention": form.cleaned_data['intention'],
                "summary": form.cleaned_data['summary'],
                "making_description": form.cleaned_data['making_description'],
                "creator_id": str(request.user.id),  # 로그인한 사용자의 ID 저장
                "target_funding": form.cleaned_data['target_funding'],
                "funding_description": form.cleaned_data['funding_description'],
                "funding_deadline": funding_deadline_datetime,
                "create_date": create_date_datetime,
                "status": "funding",
                "backers": [],
                "backers_funding": [],
                "total_funding_amount": 0,
                "payment_history": []
            }

            # GridFS에 파일 저장
            movie_file = request.FILES.get('movie_file')
            if movie_file:
                try:
                    file_id = fs.put(movie_file, filename=movie_file.name)  # GridFS에 파일 저장
                    funding_data['movie_file_id'] = file_id  # 파일 ID를 데이터에 추가
                    print("파일이 GridFS에 저장되었습니다.")
                except Exception as e:
                    print("GridFS 파일 저장 중 오류 발생:", e)
                    return render(request, 'upload_funding.html', {'form': form, 'error': '파일 저장 중 오류가 발생했습니다.'})

                # MongoDB에 데이터 저장
                try:
                    collection.insert_one(funding_data)
                    print("MongoDB 저장 완료")
                    return redirect('funding:upload_success')
                except Exception as e:
                    print("MongoDB 데이터 저장 중 오류 발생:", e)
                    return render(request, 'upload_success.html', {'form': form, 'error': '데이터 저장 중 오류가 발생했습니다.'})
            else:
                print("폼 유효성 검사 실패:", form.errors)
    else:
        form = FundingMovieForm()
    return render(request, 'upload_funding.html', {'form': form})

def funding_detail(request, movie_id):
    movie = get_object_or_404(FundingMovie, id=movie_id)
    return render(request, 'funding_detail.html', {'movie': movie})

