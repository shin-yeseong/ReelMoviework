# funding/models.py
from django.db import models
from django.contrib.auth.models import User

class FundingMovie(models.Model):
    title = models.CharField(max_length=100)
    genre = models.JSONField()  # 배열 형태로 저장
    time = models.PositiveIntegerField()  # 영화 시간 (분 단위)
    intention = models.TextField()
    summary = models.TextField()
    making_description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    target_funding = models.PositiveIntegerField()
    funding_description = models.TextField()
    funding_deadline = models.DateField()
    create_date = models.DateTimeField(auto_now_add=True)
    total_funding_amount = models.PositiveIntegerField(default=0)
    backers = models.JSONField(default=list)  # 후원자 정보 배열
    payment_history = models.JSONField(default=list)  # 결제 내역 배열

    def __str__(self):
        return self.title
