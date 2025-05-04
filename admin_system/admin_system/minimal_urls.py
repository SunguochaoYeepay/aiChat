"""
URL配置 - 最小化版本，仅用于API测试
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 只包含API路由
    path('api/', include('api.urls')),
] 