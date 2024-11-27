from bson import ObjectId
from django.utils.deprecation import MiddlewareMixin
from pymongo import MongoClient
from django.contrib.auth.hashers import check_password

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://jklas187:PI9IWptT59WMOYZF@likemovie.toohv.mongodb.net/?retryWrites=true&w=majority')
db = client['mongodatabase']
users_collection = db['user']

# 사용자 클래스 정의


from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.models import AnonymousUser


class MongoDBUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get('user_id')
        print(f"세션에서 가져온 user_id: {user_id}")  # 디버깅용

        if user_id:
            try:
                # MongoDB에서 사용자 데이터 가져오기
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                print(f"MongoDB에서 가져온 사용자 데이터: {user}")  # 디버깅용

                if user:
                    # MongoDBUser 객체 생성
                    request.user = MongoDBUser(
                        username=user['username'],
                        email=user.get('email', ''),
                        role=user.get('role', 'viewer'),
                        id=str(user['_id']),  # _id를 문자열로 변환
                        hashed_password=user.get('password'),
                        first_name=user.get('first_name', ''),
                        last_name=user.get('last_name', ''),
                        date_of_birth=user.get('date_of_birth'),
                        gender=user.get('gender', ''),
                        bank=user.get('bank', ''),
                        phone_number=user.get('phone_number', ''),
                        address=user.get('address', ''),
                        last_login=user.get('last_login'),  # last_login 추가
                        date_joined=user.get('date_joined')  # date_joined 추가
                    )
                    print(f"request.user 설정됨: {request.user.username}")
                else:
                    print("MongoDB에서 사용자를 찾을 수 없습니다.")
                    request.user = AnonymousUser()
            except Exception as e:
                print(f"MongoDBUserMiddleware 오류: {e}")
                request.user = AnonymousUser()
        else:
            print("세션에 user_id가 없습니다.")
            request.user = AnonymousUser()

class MongoDBUser:
    def __init__(self, username, email, role, id, hashed_password,
                 first_name='', last_name='', date_of_birth=None,
                 gender='', bank='', phone_number='', address='',
                 last_login=None, date_joined=None):
        self.username = username
        self.email = email
        self.role = role
        self.id = id
        self.password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.bank = bank
        self.phone_number = phone_number
        self.address = address
        self.last_login = last_login
        self.date_joined = date_joined
        self.is_authenticated = True

    def is_active(self):
        return True

    def is_staff(self):
        return self.role == 'admin'



    def check_password(self, raw_password):
        """
        Check if the provided password matches the stored hashed password.
        """
        return check_password(raw_password, self.password)
