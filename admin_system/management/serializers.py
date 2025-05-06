from rest_framework import serializers
from .models import PromptTemplate, KnowledgeBase, ServiceControl, ModelConfig, KnowledgeChunk


class PromptTemplateSerializer(serializers.ModelSerializer):
    """提示词模板序列化器"""
    
    class Meta:
        model = PromptTemplate
        fields = ['id', 'name', 'description', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PromptTemplateCategorySerializer(serializers.Serializer):
    """提示词模板分类序列化器"""
    
    category = serializers.CharField()
    types = serializers.DictField(child=serializers.CharField()) 


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """知识库序列化器"""
    
    document_count = serializers.IntegerField(read_only=True)
    is_indexed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'name', 'description', 'file_path', 
            'content', 'document_count', 'is_indexed',
            'embedding_model', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'document_count', 'is_indexed']


class KnowledgeChunkSerializer(serializers.ModelSerializer):
    """知识库分块序列化器"""
    
    class Meta:
        model = KnowledgeChunk
        fields = [
            'id', 'knowledge_base', 'content', 'is_indexed',
            'metadata', 'created_at'
        ]
        read_only_fields = ['created_at', 'is_indexed']


class ServiceControlSerializer(serializers.ModelSerializer):
    """服务控制序列化器"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ServiceControl
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'command', 'pid', 'updated_at'
        ]
        read_only_fields = ['updated_at', 'pid', 'status_display']


class ModelConfigSerializer(serializers.ModelSerializer):
    """模型配置序列化器"""
    
    device_display = serializers.CharField(source='get_device_display', read_only=True)
    precision_display = serializers.CharField(source='get_precision_display', read_only=True)
    
    class Meta:
        model = ModelConfig
        fields = [
            'id', 'name', 'model_path', 'device', 'device_display',
            'is_active', 'batch_size', 'precision', 'precision_display',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'device_display', 'precision_display'] 