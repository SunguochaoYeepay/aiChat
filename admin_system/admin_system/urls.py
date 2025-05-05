"""
URL configuration for admin_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import api_test_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # 添加API测试页面路由
    path('api/test/', api_test_view, name='api_test'),
    
    path('management/', include('management.urls')),
    path('vector/', include('vector_search.urls')),
    # 集成API应用路由
    path('api/', include('api.urls')),
    # 兼容原有FastAPI接口路由（不含api前缀）
    path('', include('api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
