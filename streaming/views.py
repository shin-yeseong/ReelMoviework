# streaming/views.py
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt

from common.views import sessions_collection, users_collection
from mongodbconnect.settings import client
from .models import StreamingMovie
from .forms import StreamingMovieForm
import uuid
from datetime import datetime
from mongodbconnect import settings
from pymongo import MongoClient
import gridfs
from bson import ObjectId

# MongoDB 클라이언트 및 GridFS 설정
# MongoDB 클라이언트 및 데이터베이스 설정
client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client_mongo['mongodatabase']  # 데이터베이스 선택
collection = db['streaming_streamingmovie']  # 컬렉션 선택
streaming_movie_fs = gridfs.GridFS(db)  # 동영상 파일용 GridFS
streaming_poster_fs = gridfs.GridFS(db)  # 포스터 이미지용 GridFS

@login_required(login_url='signin')
def upload_streaming_movie(request):
    user_role = request.user.role

    if user_role != 'host':
        return render(request, 'permission_denied.html')


    if request.method == 'POST':
        print(request.POST.getlist('genre'))  # POST 요청에서 genre 값이 어떻게 전달되는지 확인

        # POST 데이터를 복사하고 genre 필드만 빈 값 없이 설정
        data = request.POST.copy()
        data.setlist('genre', [choice for choice in request.POST.getlist('genre') if choice])

        form = StreamingMovieForm(data, request.FILES)
        print("POST 요청 수신")
        if form.is_valid():
            print("폼 유효성 검사 통과")

            # 필드 데이터 및 날짜 변환
            release_date = form.cleaned_data['release_date']
            release_date_datetime = datetime.combine(release_date, datetime.min.time())  # datetime.date -> datetime.datetime 변환
            create_date_datetime = datetime.now()

            # 영화 데이터 구조 생성
            streaming_data = {
                "s_id": str(uuid.uuid4()),
                "title": form.cleaned_data['title'],
                "genre": form.cleaned_data['genre'],
                "time": form.cleaned_data['time'],
                "actors": form.cleaned_data['actors'],
                "summary": form.cleaned_data['summary'],
                "creator_id": str(request.user.id),
                "release_date": release_date_datetime,
                "create_date": create_date_datetime,
                "views": 0,
                "payment_history": [],
                "viewer": []
            }

            # GridFS에 파일 저장
            movie_file = request.FILES.get('movie_file')
            poster_file = request.FILES.get('poster_file')
            if poster_file:
                try:
                    poster_id = streaming_poster_fs.put(poster_file, filename=poster_file.name)  # GridFS에 이미지 파일 저장
                    streaming_data['poster_image_id'] = poster_id  # 이미지 파일 ID 추가
                    print("포스터 이미지 파일이 GridFS에 저장되었습니다.")
                except Exception as e:
                    print("GridFS 이미지 파일 저장 중 오류 발생:", e)
                    return render(request, 'upload_funding.html',
                                  {'form': form, 'error': '이미지 파일 저장 중 오류가 발생했습니다.'})

            if movie_file:
                try:
                    file_id = streaming_movie_fs.put(movie_file, filename=movie_file.name)  # GridFS에 파일 저장
                    streaming_data['movie_file_id'] = file_id  # 파일 ID를 데이터에 추가
                    print("파일이 GridFS에 저장되었습니다.")
                except Exception as e:
                    print("GridFS 파일 저장 중 오류 발생:", e)
                    return render(request, 'upload_streaming.html', {'form': form, 'error': '파일 저장 중 오류가 발생했습니다.'})

                # MongoDB에 데이터 저장
                try:
                    collection.insert_one(streaming_data)
                    print("MongoDB 저장 완료")
                    return redirect('streaming:upload_streaming_success')
                except Exception as e:
                    print("MongoDB 데이터 저장 중 오류 발생:", e)
                    return render(request, 'upload_streaming_success.html', {'form': form, 'error': '데이터 저장 중 오류가 발생했습니다.'})
            else:
                print("폼 유효성 검사 실패:", form.errors)
    else:
        form = StreamingMovieForm()
    return render(request, 'upload_streaming.html', {'form': form})

def streaming_detail(request, movie_id):
    movie = get_object_or_404(StreamingMovie, id=movie_id)
    return render(request, 'streaming_detail.html', {'movie': movie})

def get_streaming_movie_poster_image(request, poster_id):
    try:
        # ObjectId로 변환하여 파일 가져오기
        poster_object_id = ObjectId(poster_id)
        file = streaming_poster_fs.get(poster_object_id)
        # 파일 형식에 따라 Content-Type 동적으로 설정
        content_type = "image/jpeg"
        if file.filename.endswith('.png'):
            content_type = "image/png"
        elif file.filename.endswith('.gif'):
            content_type = "image/gif"
        elif file.filename.endswith('.jpg') or file.filename.endswith('.jpeg'):
            content_type = "image/jpeg"

        image_data = file.read()
        return HttpResponse(image_data, content_type=content_type)
    except gridfs.errors.NoFile:
        print(f"Image with poster_id {poster_id} not found in GridFS")
        return HttpResponse(status=404)  # 파일이 없으면 404 반환
    except Exception as e:
        print(f"Error retrieving image: {e}")
        return HttpResponse(status=500)  # 다른 오류가 있으면 500 반환

def streaming_movie_list(request):
    # MongoDB에서 모든 영화 정보를 가져옵니다.
    movies = list(collection.find())
    return render(request, 'streaming_movie_list.html', {'movies': movies})

@login_required(login_url='signin')
def streaming_movie_detail(request, movie_id):
    try:
        # UUID로 저장된 경우 문자열로 조회
        movie = collection.find_one({"s_id": movie_id})
        # ObjectId 형식으로 저장된 경우 ObjectId로 조회
        if not movie:
            movie = collection.find_one({"_id": ObjectId(movie_id)})
    except Exception as e:
        print("오류 발생:", e)
        raise Http404("Movie not found")

    # 영화 정보가 없을 경우 404 반환
    if not movie:
        raise Http404("Movie not found")

    # GridFS에서 파일 가져오기
    file_id = movie.get("movie_file_id")
    if file_id and streaming_movie_fs.exists(file_id):
        movie_file = streaming_movie_fs.get(file_id)
        response = FileResponse(movie_file, content_type='video/mp4')
        response['Content-Disposition'] = f'inline; filename="{movie["title"]}.mp4"'
        return response
    else:
        raise Http404("Video file not found")

# 영화 목록 API 엔드포인트
def movie_list(request):
    movies = []
    for movie in collection.find():
        movies.append({
            "s_id": str(movie["s_id"]),
            "title": movie["title"],
            "genre": movie["genre"],
            "time": movie["time"],
            "summary": movie["summary"],
            "release_date": movie["release_date"],
            "views": movie["views"],
            "movie_file_id": str(movie["movie_file_id"]),
            "poster_image_id": str(movie.get("poster_image_id"))  # 수정된 부분
        })
    return JsonResponse(movies, safe=False)

# 영화 상세 정보 API 엔드포인트
def movie_detail(request, movie_id):
    movie = collection.find_one({"s_id": movie_id})
    if movie:
        movie_data = {
            "s_id": str(movie["s_id"]),
            "title": movie["title"],
            "genre": movie["genre"],
            "time": movie["time"],
            "summary": movie["summary"],
            "release_date": movie["release_date"],
            "views": movie["views"],
            "movie_file_id": str(movie["movie_file_id"]),
            "movie_poster_id": str(movie["poster_image_id"])
        }
        return JsonResponse(movie_data)
    return JsonResponse({"error": "Movie not found"}, status=404)
