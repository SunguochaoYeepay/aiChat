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
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '知识库'
        verbose_name_plural = '知识库'
    
    def __str__(self):
        return self.name
