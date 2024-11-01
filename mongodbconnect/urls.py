"""
URL configuration for mongodbconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# mongodbconnect/urls.py
from django.contrib import admin
from django.urls import path, include
from main_page.views import home  # 홈 페이지 뷰 임포트 (myapp을 실제 앱 이름으로 대체)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('streaming/', include('streaming.urls')),
    path('funding/', include('funding.urls')),
    path('', home, name='home'),  # 루트 URL
]