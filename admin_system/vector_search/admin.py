from django.contrib import admin
from .models import VectorIndex, DocumentVector
from django.utils.html import format_html
from django.urls import reverse

@admin.register(VectorIndex)
class VectorIndexAdmin(admin.ModelAdmin):
    """向量索引管理"""
    list_display = ('name', 'description', 'document_count', 'vector_dimension', 'last_updated')
    search_fields = ('name', 'description')
    readonly_fields = ('document_count', 'last_updated', 'vector_file', 'metadata_file')
    
    actions = ['rebuild_index']
    
    def rebuild_index(self, request, queryset):
        """重建向量索引"""
        from .utils import rebuild_vector_index
        
        for index in queryset:
            rebuild_vector_index(index)
            self.message_user(request, f"索引 '{index.name}' 已重建")
    
    rebuild_index.short_description = "重建选中的向量索引"

@admin.register(DocumentVector)
class DocumentVectorAdmin(admin.ModelAdmin):
    """文档向量管理"""
    list_display = ('document_id', 'source', 'text_preview', 'index', 'embedding_updated')
    list_filter = ('index', 'source', 'embedding_updated')
    search_fields = ('document_id', 'text', 'source')
    
    def text_preview(self, obj):
        """文本预览"""
        if len(obj.text) > 100:
            return obj.text[:100] + '...'
        return obj.text
    
    text_preview.short_description = '文本内容'
