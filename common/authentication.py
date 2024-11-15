from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model

User = get_user_model()

class MongoBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 'user' 컬렉션에서 사용자 찾기
            user = User.objects.get(username=username)
            if user and check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, username=None):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
