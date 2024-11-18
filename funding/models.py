# funding/models.py
from django.db import models
from django.contrib.auth.models import User
from bson import ObjectId  # MongoDB ObjectId를 사용하기 위해 import

class FundingMovie(models.Model):
    title = models.CharField(max_length=100)
    genre = models.JSONField()  # 배열 형태로 저장
    time = models.PositiveIntegerField()  # 영화 시간 (분 단위)
    intention = models.TextField()
    summary = models.TextField()
    making_description = models.TextField()
    creator = models.CharField(max_length=100)  # director's name
    actors = models.JSONField(default=list)  # list of lead actors
    creator_talk = models.TextField()  # director's message (combined with summary)
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE)
    target_funding = models.PositiveIntegerField()
    funding_description = models.TextField()
    funding_deadline = models.DateField()
    create_date = models.DateTimeField(auto_now_add=True)
    total_funding_amount = models.PositiveIntegerField(default=0)
    backers = models.JSONField(default=list)  # 후원자 정보 배열
    payment_history = models.JSONField(default=list)  # 결제 내역 배열
    movie_file_id = models.CharField(max_length=255, blank=True, null=True)  # 동영상 파일 ID
    poster_file_id = models.CharField(max_length=255, blank=True, null=True)  # 포스터 이미지 파일 ID

    funding_options = models.JSONField(default=list)  # 여러 옵션 저장

    def __str__(self):
        return self.title
