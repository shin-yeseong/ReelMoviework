from django.urls import path
from common import views

urlpatterns = [
    # account 관련 URL
    path('', views.account, name="account_do"),
    path('send', views.send, name="email_send"),

    # main 관련 URL
    path('signup', views.signup, name="main_signup"),
    path('signup/join', views.join, name="main_join"),
    path('signin', views.signin, name="main_signin"),
    path('verifyCode', views.verifyCode, name="main_verifyCode"),
    path('verify', views.verify, name="main_verify"),
    path('result', views.result, name="main_result"),
]