"""
API路由配置 - 提供与原系统兼容的URL路由

此模块实现了与原有FastAPI系统兼容的URL配置，确保现有前端能继续正常工作。
"""
from django.urls import path
from . import views

urlpatterns = [
    # 原有API接口
    path('analyze', views.analyze_image, name='api_analyze_image'),
    path('v1/chat/completions', views.chat_completions, name='api_chat_completions'),
    path('search', views.search_knowledge_base, name='api_search_kb'),
    path('status', views.get_service_status, name='api_service_status'),
] 