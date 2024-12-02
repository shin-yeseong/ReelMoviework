# main_page/views.py
from django.shortcuts import render
from pymongo import MongoClient
from django.conf import settings
import gridfs
import base64
from gridfs.errors import NoFile  # NoFile 예외를 gridfs.errors에서 가져옴



client_mongo = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client_mongo['mongodatabase']  # 실제 MongoDB 데이터베이스 이름
collection = db['funding_fundingmovie']  # 펀딩 영화 컬렉션

movie_fs = gridfs.GridFS(db)  # 동영상 파일용 GridFS
poster_fs = gridfs.GridFS(db)  # 포스터 이미지용 GridFS



# 메인 페이지 뷰
def home(request):
    # 펀딩 영화 중에서 랜덤으로 3개를 가져오기
    funding_movies = collection.aggregate([
        {"$match": {"status": "funding"}},  # 'funding' 상태의 영화만 선택
        {"$sample": {"size": 3}}  # 3개의 랜덤 영화 선택
    ])

    movies_list = []
    for movie in funding_movies:
        # 포스터 이미지 ID 가져오기
        poster_id = movie.get('poster_image_id')
        if poster_id:
            try:
                poster_file = poster_fs.get(poster_id)
                if isinstance(poster_file, gridfs.grid_file.GridOut):
                    image_data = base64.b64encode(poster_file.read()).decode('utf-8')
                    movie['image_data'] = image_data
                else:
                    print(f"Invalid file format for poster_id {poster_id}")
                    movie['image_data'] = None
            except NoFile:
                print(f"No file found for poster_id {poster_id}")
                movie['image_data'] = None
            except Exception as e:
                print(f"Error retrieving poster image: {e}")
                movie['image_data'] = None

        movies_list.append(movie)

    return render(request, 'home.html', {'movies': movies_list})
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

def dashboard(request):
    return render(request, 'dashboard.html')




