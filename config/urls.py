from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('', include('apps.users.urls')),
]

if settings.DEBUG:
    # gunicorn 不会自动托管静态文件（runserver 才会），这里显式挂载，
    # 否则容器里 /static/css/style.css 等 404，页面没有样式。
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
