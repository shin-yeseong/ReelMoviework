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
        print(f"user_id from session: {user_id}")  # 디버깅



        if user_id:
            try:
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                if user:
                    # MongoDBUser 객체 생성 시 password 속성 추가
                    request.user = MongoDBUser(
                        username=user['username'],
                        email=user['email'],
                        role=user.get('role', 'viewer'),
                        id=user['_id'],
                        hashed_password=user.get('password')  # 여기서 비밀번호 해시 추가
                    )
                    print(f"request.user set to: {request.user.username}")
                else:
                    print("User not found in MongoDB")
                    request.user = AnonymousUser()
            except Exception as e:
                print(f"Error in MongoDBUserMiddleware: {e}")
                request.user = AnonymousUser()
        else:
            print("No user_id in session")
            request.user = AnonymousUser()


class MongoDBUser:
    def __init__(self, username, email, role, id, hashed_password):
        self.username = username
        self.email = email
        self.role = role
        self.id = str(id)
        self.is_authenticated = True
        self.password = hashed_password  # 비밀번호 해시 저장

    def is_active(self):
        return True

    def is_staff(self):
        return self.role == 'admin'

    def check_password(self, raw_password):
        """
        Check if the provided password matches the stored hashed password.
        """
        return check_password(raw_password, self.password)

    def change_password(self, new_password):
        """
        Change the user's password.
        """
        hashed_password = make_password(new_password)  # 비밀번호 해싱
        users_collection.update_one(
            {'_id': ObjectId(self.id)},  # MongoDB에서 사용자 검색
            {'$set': {'password': hashed_password}}  # 새 비밀번호 저장
        )
        self.password = hashed_password  # 객체의 비밀번호도 업데이트



