from django.contrib import admin
from django.utils.html import format_html
import subprocess
import os
from .models import ServiceControl, PromptTemplate, KnowledgeBase
from django.urls import reverse, path
from django.contrib.admin import AdminSite

@admin.register(ServiceControl)
class ServiceControlAdmin(admin.ModelAdmin):
    """服务控制的管理配置"""
    list_display = ('name', 'description', 'status_tag', 'command', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    actions = ['start_service', 'stop_service']
    
    def status_tag(self, obj):
        """将状态显示为彩色标签"""
        if obj.status == 'running':
            return format_html('<span style="background-color:#28a745; color:white; padding:2px 8px; border-radius:4px;">运行中</span>')
        else:
            return format_html('<span style="background-color:#dc3545; color:white; padding:2px 8px; border-radius:4px;">已停止</span>')
    status_tag.short_description = '状态'
    
    def start_service(self, request, queryset):
        """启动服务操作"""
        for service in queryset:
            try:
                # 实际中应该使用更安全的方式执行命令
                # 这里仅作为示例
                process = subprocess.Popen(service.command, shell=True)
                service.pid = process.pid
                service.status = 'running'
                service.save()
            except Exception as e:
                self.message_user(request, f"启动服务 {service.name} 时出错: {str(e)}")
                continue
        self.message_user(request, f"已尝试启动 {queryset.count()} 个服务")
    start_service.short_description = "启动所选服务"
    
    def stop_service(self, request, queryset):
        """停止服务操作"""
        for service in queryset:
            try:
                # 实际使用中需要实现正确的服务停止逻辑
                # 这里仅作为示例
                if os.name == 'nt':  # Windows
                    os.system(f"taskkill /F /PID {service.pid}")
                else:  # Linux/Unix
                    os.system(f"pkill -f '{service.command}'")
                service.status = 'stopped'
                service.save()
            except Exception as e:
                self.message_user(request, f"停止服务 {service.name} 时出错: {str(e)}")
                continue
        self.message_user(request, f"已尝试停止 {queryset.count()} 个服务")
    stop_service.short_description = "停止所选服务"

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    """提示词模板的管理配置"""
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'content')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('模板内容', {
            'fields': ('content',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    """知识库的管理配置"""
    list_display = ('name', 'description', 'document_count', 'file_path', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'content')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('document_count', 'created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'file_path')
        }),
        ('文档内容', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('统计信息', {
            'fields': ('document_count',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# 自定义Admin站点标题和页脚
admin.site.site_header = 'AI助手管理系统'
admin.site.site_title = 'AI助手管理'
admin.site.index_title = '管理中心'

# 添加自定义链接到Admin菜单
from django.urls import reverse

# 保存原始get_app_list方法
original_get_app_list = admin.AdminSite.get_app_list

def custom_get_app_list(self, request):
    """
    添加自定义链接到Admin菜单
    """
    app_list = original_get_app_list(self, request)
    
    # 添加提示词编辑器和导入知识库链接
    app_list.append({
        'name': '工具',
        'app_label': 'tools',
        'models': [{
            'name': '提示词编辑器',
            'object_name': 'prompteditor',
            'admin_url': reverse('prompt_editor'),
            'view_only': True,
        }, {
            'name': '导入知识库',
            'object_name': 'importkb',
            'admin_url': reverse('import_knowledge_base'),
            'view_only': True,
        }, {
            'name': '向量搜索',
            'object_name': 'vectorsearch',
            'admin_url': reverse('vector_search_ui'),
            'view_only': True,
        }]
    })
    
    return app_list

# 替换方法
admin.AdminSite.get_app_list = custom_get_app_list
