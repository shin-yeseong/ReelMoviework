from django.urls import path
from . import views

urlpatterns = [
    path('payment/checkout/', views.payment_checkout, name='payment_checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('streaming/payment/', views.streaming_payment, name='streaming_payment'),
    path('check_payment_status/<str:s_id>/', views.check_payment_status, name='check_payment_status'),
    path('streaming/play/<str:s_id>/', views.play_or_pay, name='play_or_pay'),
]