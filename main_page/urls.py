# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main_page.views import home  # 홈 페이지 뷰 임포트

urlpatterns = [
    path('admin/', admin.site.urls),
    path('streaming/', include('streaming.urls')),
    path('funding/', include('funding.urls')),
    path('common/', include('common.urls')),
    path('', home, name='home'),  # 루트 URL에 홈 페이지 추가
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)