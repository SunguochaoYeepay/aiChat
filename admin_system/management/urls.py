from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # Vue 应用视图
    path('vue/', views.VueAppView.as_view(), name='vue_app'),
    
    # 传统视图
    path('', views.management_index, name='index'),
    path('knowledge-base/', views.knowledge_base, name='knowledge_base'),
    path('service-control/', views.service_control, name='service_control'),
    path('models-config/', views.models_config, name='models_config'),
    path('save-model-config/', views.save_model_config, name='save_model_config'),
    path('prompt-manager/', views.prompt_manager, name='prompt_manager'),
    path('prompt-editor/', views.prompt_editor, name='prompt_editor'),
    path('import-kb/', views.import_knowledge_base, name='import_kb'),
    path('model-status/', views.model_service_status, name='model_status'),
    path('reload-model/', views.reload_model, name='reload_model'),
    path('vector-search/', views.vector_search_ui, name='vector_search'),
    
    # API 视图
    path('api/prompt-templates/', views.prompt_templates, name='prompt_templates'),
    path('api/get-templates-list/', views.get_templates_list, name='get_templates_list'),
    path('api/get-template/<int:template_id>/', views.get_template, name='get_template'),
    path('api/create-template/', views.create_template, name='create_template'),
    path('api/update-template/<int:template_id>/', views.update_template, name='update_template'),
    path('api/delete-template/<int:template_id>/', views.delete_template, name='delete_template'),
    path('api/refresh-templates/', views.refresh_templates, name='refresh_templates'),
    path('api/manage-service/<str:action>/', views.manage_service, name='manage_service'),
] 