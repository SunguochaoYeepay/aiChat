from django.urls import path
from . import views

urlpatterns = [
    path('import-knowledge-base/', views.import_knowledge_base, name='import_knowledge_base'),
    path('service/<str:action>/', views.manage_service, name='manage_service'),
    path('prompt-editor/', views.prompt_editor, name='prompt_editor'),
    path('prompt_templates/', views.prompt_templates, name='prompt_templates'),
    path('refresh_templates/', views.refresh_templates, name='refresh_templates'),
] 