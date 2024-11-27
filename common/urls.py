from . import views
from django.urls import path, include


from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login-success/', views.login_success, name='login_success'),
    path('mypage/', include('mypage.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),


]
