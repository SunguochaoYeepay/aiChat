"""
API路由配置 - 提供与原系统兼容的URL路由

此模块实现了与原有FastAPI系统兼容的URL配置，确保现有前端能继续正常工作。
"""
from django.urls import path
from . import views
from . import api_key_views

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

    # API 元数据端点
    path('v1/endpoints', views.endpoints, name='api_endpoints'),
    path('v1/api-keys', api_key_views.api_keys, name='api_keys'),
    
    # API密钥管理接口
    path('v1/api-keys/create', api_key_views.create_api_key, name='create_api_key'),
    path('v1/api-keys/<int:key_id>/update', api_key_views.update_api_key, name='update_api_key'),
    path('v1/api-keys/<int:key_id>/delete', api_key_views.delete_api_key, name='delete_api_key'),
    
    # 用户认证相关接口
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/logout/', views.user_logout, name='user_logout'),
    path('auth/user/', views.user_info, name='user_info'),
    path('auth/users/', views.user_list, name='user_list'),
    path('auth/users/create/', views.user_create, name='user_create'),
    path('auth/users/<int:user_id>/update/', views.user_update, name='user_update'),
    path('auth/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
] 