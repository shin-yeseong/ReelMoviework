# streaming/models.py
from django.db import models
from django.contrib.auth.models import User

class StreamingMovie(models.Model):
    title = models.CharField(max_length=100)
    genre = models.JSONField()  # 배열 형태로 저장
    time = models.PositiveIntegerField()  # 영화 시간 (분 단위)
    actors = models.TextField()
    summary = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    release_date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    payment_history = models.JSONField(default=list)  # 결제 내역 저장
    viewers = models.ManyToManyField(User, related_name='viewed_movies', blank=True)

    def __str__(self):
        return self.title