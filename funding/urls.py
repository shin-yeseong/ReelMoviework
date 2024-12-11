# funding/urls.py
from django.urls import path
from . import views

app_name = 'funding'

urlpatterns = [
    path('upload/', views.upload_funding_movie, name='upload_funding_movie'),
    path('<str:movie_id>/', views.funding_detail, name='movie_detail'),
    path('movie/list/', views.movie_list, name='movie_list'),
    path('poster/<str:poster_id>/', views.get_poster_image, name="get_poster_image"),
    path('funding-page/', views.funding_page, name='funding_movie_page'),
    path('payment/success/', views.funding_payment_success, name='funding_success'),
    path('payment/fail/', views.funding_payment_fail, name='funding_fail'),
    path('check_payment_status/<str:movie_id>/<str:order_name>/', views.check_payment_status, name='check_payment_status'),
    path('funding/funding_home/', views.funding_home, name='funding_home'),
    path('webhook/', views.funding_webhook, name='funding_webhook'),  # 웹훅 엔드포인트
]
