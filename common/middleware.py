from bson import ObjectId
from django.utils.deprecation import MiddlewareMixin
from pymongo import MongoClient

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://jklas187:PI9IWptT59WMOYZF@likemovie.toohv.mongodb.net/?retryWrites=true&w=majority')
db = client['mongodatabase']
users_collection = db['user']

# 사용자 클래스 정의


from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.models import AnonymousUser

class MongoDBUser:
    def __init__(self, username, email, role, id):
        self.username = username
        self.email = email
        self.role = role
        self.id = str(id)
        self.is_authenticated = True

    def is_active(self):
        return True

    def is_staff(self):
        return self.role == 'admin'


class MongoDBUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get('user_id')
        print(f"user_id from session: {user_id}")  # 디버깅

        if user_id:
            try:
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                if user:
                    request.user = MongoDBUser(
                        username=user['username'],
                        email=user['email'],  # 이메일 추가
                        role=user.get('role', 'viewer'),  # 역할 추가
                        id=user['_id']
                    )
                    print(f"request.user set to: {request.user.username}")  # 디버깅
                else:
                    print("User not found in MongoDB")
                    request.user = AnonymousUser()
            except Exception as e:
                print(f"Error in MongoDBUserMiddleware: {e}")
                request.user = AnonymousUser()
        else:
            print("No user_id in session")
            request.user = AnonymousUser()

