from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='main_signup'),
    path('signin/', views.signin, name='main_signin'),
    path('profile/', views.profile, name='account_profile'),
    path('send_email/', views.send_email, name='email_send'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
]