"""
API路由配置 - 提供与原系统兼容的URL路由

此模块实现了与原有FastAPI系统兼容的URL配置，确保现有前端能继续正常工作。
"""
from django.urls import path
from . import views

urlpatterns = [
    # 首页路由
    path('', views.index_view, name='index'),
    # 原有API接口
    path('analyze', views.analyze_image, name='api_analyze_image'),
    path('v1/chat/completions', views.chat_completions, name='api_chat_completions'),
    path('search', views.search_knowledge_base, name='api_search_kb'),
    path('status', views.get_service_status, name='api_service_status'),
    
    # API管理界面
    path('docs/', views.api_docs_view, name='api_docs'),
    path('import/', views.api_import_view, name='api_import'),
    
    # API测试相关接口
    path('test/', views.api_test_view, name='api_test'),
    path('endpoint/<int:endpoint_id>/', views.api_endpoint_detail, name='api_endpoint_detail'),
    path('test/execute/', views.api_test_execute, name='api_test_execute'),
] 