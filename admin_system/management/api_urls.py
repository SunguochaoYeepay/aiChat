from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PromptTemplateViewSet, 
    KnowledgeBaseViewSet,
    KnowledgeChunkViewSet,
    ServiceControlViewSet,
    ModelConfigViewSet,
    DashboardViewSet
)

router = DefaultRouter()
router.register(r'templates', PromptTemplateViewSet)
router.register(r'knowledge', KnowledgeBaseViewSet)
router.register(r'chunks', KnowledgeChunkViewSet)
router.register(r'services', ServiceControlViewSet)
router.register(r'models', ModelConfigViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
] 