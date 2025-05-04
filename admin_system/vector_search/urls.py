from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.vector_search_ui, name='vector_search_ui'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/import-kb/', views.api_import_kb, name='api_import_kb'),
    path('api/import-prompts/', views.api_import_prompt_templates, name='api_import_prompts'),
    path('api/import-all/', views.api_import_all, name='api_import_all'),
] 