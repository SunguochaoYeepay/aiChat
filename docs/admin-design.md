# Django Admin后台管理系统设计方案

## 1. 基础架构
- 使用Django原生Admin系统
- 添加Simpleui美化界面
- 设计适合管理知识库和服务的模型

## 2. 模型设计
```python
# models.py
from django.db import models

class ServiceControl(models.Model):
    """服务控制模型"""
    STATUS_CHOICES = (
        ('running', '运行中'),
        ('stopped', '已停止'),
    )
    
    name = models.CharField('服务名称', max_length=100)
    description = models.TextField('服务描述', blank=True)
    status = models.CharField('服务状态', max_length=20, choices=STATUS_CHOICES, default='stopped')
    command = models.CharField('启动命令', max_length=500)
    last_updated = models.DateTimeField('最后更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '服务管理'
        verbose_name_plural = '服务管理'

class PromptTemplate(models.Model):
    """提示词模板"""
    name = models.CharField('模板名称', max_length=100)
    description = models.TextField('模板描述', blank=True)
    content = models.TextField('提示词内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '提示词库'
        verbose_name_plural = '提示词库'

class KnowledgeBase(models.Model):
    """知识库"""
    name = models.CharField('知识库名称', max_length=100)
    description = models.TextField('知识库描述', blank=True)
    document_count = models.IntegerField('文档数量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '知识库管理'
        verbose_name_plural = '知识库管理'
```

## 3. Admin配置
```python
# admin.py
from django.contrib import admin
import subprocess
import os
from .models import ServiceControl, PromptTemplate, KnowledgeBase

@admin.register(ServiceControl)
class ServiceControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'status', 'last_updated')
    search_fields = ('name', 'description')
    actions = ['start_service', 'stop_service']
    
    def start_service(self, request, queryset):
        for service in queryset:
            if service.status != 'running':
                try:
                    # 执行启动命令
                    subprocess.Popen(service.command, shell=True)
                    service.status = 'running'
                    service.save()
                except Exception as e:
                    self.message_user(request, f"启动服务 {service.name} 失败: {str(e)}")
        self.message_user(request, "所选服务已启动")
    start_service.short_description = "启动选中的服务"
    
    def stop_service(self, request, queryset):
        for service in queryset:
            if service.status == 'running':
                try:
                    # 根据服务名称获取进程ID并终止
                    os.system(f"pkill -f '{service.command}'")
                    service.status = 'stopped'
                    service.save()
                except Exception as e:
                    self.message_user(request, f"停止服务 {service.name} 失败: {str(e)}")
        self.message_user(request, "所选服务已停止")
    stop_service.short_description = "停止选中的服务"

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'content', 'description')
    list_filter = ('created_at',)
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('提示词内容', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
    )

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'document_count', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('document_count',)
```

## 4. 安装Simpleui美化界面
```bash
pip install django-simpleui
```

添加到settings.py的INSTALLED_APPS中:
```python
INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    # 其他应用...
]
```

## 5. Admin界面定制
```python
# 在admin.py中添加以下配置
admin.site.site_header = '管理系统'
admin.site.site_title = '服务与知识库管理'
admin.site.index_title = '管理控制台'
```

## 6. 可扩展的设计
该方案只是基础实现，未来可以根据需要扩展：
- 增加知识库文档上传功能
- 添加服务状态检测功能
- 增加日志查看功能
- 创建自定义的Dashboard显示服务状态

## 7. 实施计划
1. 创建Django应用
2. 实现基础模型
3. 配置Admin界面
4. 添加服务管理功能
5. 集成提示词管理
6. 实现知识库管理
7. 美化界面
8. 测试与部署 