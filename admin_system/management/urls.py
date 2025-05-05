from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('import-knowledge-base/', views.import_knowledge_base, name='import_knowledge_base'),
    path('service/<str:action>/', views.manage_service, name='manage_service'),
    path('prompt-editor/', views.prompt_editor, name='prompt_editor'),
    path('prompt_templates/', views.prompt_templates, name='prompt_templates'),
    path('refresh_templates/', views.refresh_templates, name='refresh_templates'),
    path('model_service_status/', views.model_service_status, name='model_service_status'),
    path('reload_model/', views.reload_model, name='reload_model'),
    path('vector-search/', views.vector_search_ui, name='vector_search_ui'),
] 