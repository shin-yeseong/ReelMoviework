from django.urls import path
from . import views



urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login-success/', views.login_success, name='login_success'),
    path('logout/', views.logout_view, name='logout'),


]
