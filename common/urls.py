from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('profile/', views.profile, name='profile'),
    #path('send_email/', views.send_email, name='email_send'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
]