from django.db import models

# Create your models here.

class ServiceControl(models.Model):
    """服务控制模型"""
    STATUS_CHOICES = (
        ('running', '运行中'),
        ('stopped', '已停止'),
    )
    
    name = models.CharField('服务名称', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='stopped')
    command = models.CharField('启动命令', max_length=255)
    pid = models.IntegerField('进程ID', blank=True, null=True)
    updated_at = models.DateTimeField('最后更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '服务控制'
        verbose_name_plural = '服务控制'
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

class PromptTemplate(models.Model):
    """提示词模板模型"""
    name = models.CharField('模板名称', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    content = models.TextField('内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '提示词模板'
        verbose_name_plural = '提示词模板'
    
    def __str__(self):
        return self.name

class KnowledgeBase(models.Model):
    """知识库模型"""
    name = models.CharField('知识库名称', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    document_count = models.IntegerField('文档数量', default=0)
    file_path = models.CharField('文件路径', max_length=255, blank=True, null=True)
    content = models.TextField('文档内容', blank=True, null=True)
    vector_data = models.BinaryField('向量数据', blank=True, null=True)
    is_indexed = models.BooleanField('是否已向量化', default=False)
    embedding_model = models.CharField('嵌入模型', max_length=100, default='text-embedding-ada-002')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '知识库'
        verbose_name_plural = '知识库'
    
    def __str__(self):
        return self.name
    
    @property
    def chunks(self):
        """获取知识库的所有分块"""
        return self.knowledgechunk_set.all()
    
    def update_document_count(self):
        """更新文档数量"""
        self.document_count = self.chunks.count()
        self.save(update_fields=['document_count'])

class KnowledgeChunk(models.Model):
    """知识库分块模型，用于更细粒度的检索"""
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, verbose_name='所属知识库')
    content = models.TextField('分块内容')
    vector_data = models.BinaryField('向量数据', blank=True, null=True)
    is_indexed = models.BooleanField('是否已向量化', default=False)
    metadata = models.JSONField('元数据', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '知识分块'
        verbose_name_plural = '知识分块'
        ordering = ['knowledge_base', 'id']
    
    def __str__(self):
        return f"{self.knowledge_base.name}的分块 #{self.id}"

class ModelConfig(models.Model):
    """模型配置"""
    DEVICE_CHOICES = (
        ('cuda', 'GPU'),
        ('cpu', 'CPU'),
    )
    
    PRECISION_CHOICES = (
        ('float16', '半精度'),
        ('float32', '全精度'),
    )
    
    name = models.CharField('配置名称', max_length=100)
    model_path = models.CharField('模型路径', max_length=255)
    device = models.CharField('设备', max_length=20, choices=DEVICE_CHOICES, default='cuda')
    is_active = models.BooleanField('是否激活', default=False)
    batch_size = models.IntegerField('批处理大小', default=1)
    precision = models.CharField('精度', max_length=20, choices=PRECISION_CHOICES, default='float16')
    description = models.TextField('描述', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '模型配置'
        verbose_name_plural = '模型配置'
    
    def __str__(self):
        return f"{self.name} ({self.get_device_display()})"
    
    def save(self, *args, **kwargs):
        """保存时确保只有一个激活的配置"""
        if self.is_active:
            # 将其他配置设为非激活
            ModelConfig.objects.all().update(is_active=False)
        
        super().save(*args, **kwargs)
