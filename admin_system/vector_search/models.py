from django.db import models
import json
import numpy as np
import os
from django.conf import settings

class VectorIndex(models.Model):
    """向量索引模型"""
    name = models.CharField('索引名称', max_length=100, unique=True)
    description = models.TextField('描述', blank=True, null=True)
    document_count = models.IntegerField('文档数量', default=0)
    vector_dimension = models.IntegerField('向量维度', default=384)  # sentence-transformers默认维度
    last_updated = models.DateTimeField('最后更新时间', auto_now=True)
    vector_file = models.CharField('向量文件路径', max_length=255, blank=True, null=True)
    metadata_file = models.CharField('元数据文件路径', max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = '向量索引'
        verbose_name_plural = '向量索引'
    
    def __str__(self):
        return f"{self.name} ({self.document_count}文档)"
    
    def get_index_directory(self):
        """获取索引文件存储目录"""
        base_dir = os.path.join(settings.BASE_DIR, 'vector_indices')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return base_dir
    
    def get_vector_file_path(self):
        """获取向量文件路径"""
        if not self.vector_file:
            self.vector_file = os.path.join(self.get_index_directory(), f"{self.name}_vectors.npy")
            self.save(update_fields=['vector_file'])
        return self.vector_file
    
    def get_metadata_file_path(self):
        """获取元数据文件路径"""
        if not self.metadata_file:
            self.metadata_file = os.path.join(self.get_index_directory(), f"{self.name}_metadata.json")
            self.save(update_fields=['metadata_file'])
        return self.metadata_file

class DocumentVector(models.Model):
    """文档向量模型"""
    index = models.ForeignKey(VectorIndex, on_delete=models.CASCADE, related_name='documents', verbose_name='所属索引')
    document_id = models.CharField('文档ID', max_length=100)
    source = models.CharField('来源', max_length=100)
    text = models.TextField('文本内容')
    metadata = models.JSONField('元数据', blank=True, null=True)
    embedding_updated = models.DateTimeField('向量更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '文档向量'
        verbose_name_plural = '文档向量'
        unique_together = ('index', 'document_id')
    
    def __str__(self):
        return f"{self.source}:{self.document_id}"
