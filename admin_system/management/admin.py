from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
import subprocess
import os
from .models import ServiceControl, PromptTemplate, KnowledgeBase, ModelConfig, KnowledgeChunk
from django.urls import reverse, path
from django.contrib.admin import AdminSite
from django.urls import reverse

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
    list_display = ('name', 'description', 'document_count', 'is_indexed_tag', 'file_path', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'content')
    list_filter = ('is_indexed', 'created_at', 'updated_at')
    readonly_fields = ('document_count', 'is_indexed', 'created_at', 'updated_at')
    actions = ['process_knowledge_base']
    
    def is_indexed_tag(self, obj):
        """将索引状态显示为彩色标签"""
        if obj.is_indexed:
            return format_html('<span style="background-color:#28a745; color:white; padding:2px 8px; border-radius:4px;">已索引</span>')
        else:
            return format_html('<span style="background-color:#dc3545; color:white; padding:2px 8px; border-radius:4px;">未索引</span>')
    is_indexed_tag.short_description = '索引状态'
    
    def process_knowledge_base(self, request, queryset):
        """处理选中的知识库"""
        from knowledge_base.services import process_knowledge_base
        
        success_count = 0
        for kb in queryset:
            try:
                if process_knowledge_base(kb.id):
                    success_count += 1
            except Exception as e:
                self.message_user(request, f"处理知识库 {kb.name} 时出错: {str(e)}", level='error')
                continue
        
        self.message_user(request, f"已成功处理 {success_count}/{queryset.count()} 个知识库")
    process_knowledge_base.short_description = "处理并索引选中的知识库"
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'file_path')
        }),
        ('文档内容', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('索引信息', {
            'fields': ('document_count', 'is_indexed', 'embedding_model')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('process/<int:kb_id>/', self.admin_site.admin_view(self.process_kb_view), name='process_knowledge_base'),
        ]
        return custom_urls + urls
    
    def process_kb_view(self, request, kb_id):
        """知识库处理视图"""
        try:
            from knowledge_base.services import process_knowledge_base
            kb = KnowledgeBase.objects.get(id=kb_id)
            
            if process_knowledge_base(kb_id):
                self.message_user(request, f"知识库 '{kb.name}' 处理成功")
            else:
                self.message_user(request, f"知识库 '{kb.name}' 处理失败", level='error')
                
        except KnowledgeBase.DoesNotExist:
            self.message_user(request, f"知识库ID {kb_id} 不存在", level='error')
        except Exception as e:
            self.message_user(request, f"处理知识库时出错: {str(e)}", level='error')
        
        # 重定向回知识库列表
        return redirect('admin:management_knowledgebase_changelist')

@admin.register(ModelConfig)
class ModelConfigAdmin(admin.ModelAdmin):
    """模型配置的管理配置"""
    list_display = ('name', 'model_path', 'device_tag', 'is_active_tag', 'precision', 'batch_size', 'updated_at')
    list_filter = ('device', 'is_active', 'precision', 'created_at')
    search_fields = ('name', 'description', 'model_path')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['activate_model', 'reload_model']
    
    def device_tag(self, obj):
        """将设备显示为彩色标签"""
        if obj.device == 'cuda':
            return format_html('<span style="background-color:#17a2b8; color:white; padding:2px 8px; border-radius:4px;">GPU</span>')
        else:
            return format_html('<span style="background-color:#6c757d; color:white; padding:2px 8px; border-radius:4px;">CPU</span>')
    device_tag.short_description = '设备'
    
    def is_active_tag(self, obj):
        """将激活状态显示为彩色标签"""
        if obj.is_active:
            return format_html('<span style="background-color:#28a745; color:white; padding:2px 8px; border-radius:4px;">激活</span>')
        else:
            return format_html('<span style="background-color:#dc3545; color:white; padding:2px 8px; border-radius:4px;">未激活</span>')
    is_active_tag.short_description = '是否激活'
    
    def activate_model(self, request, queryset):
        """将所选模型设为激活状态"""
        if queryset.count() > 1:
            self.message_user(request, "一次只能激活一个模型配置", level='error')
            return
        
        # 将所有模型配置设为非激活
        ModelConfig.objects.all().update(is_active=False)
        
        # 激活所选模型配置
        model_config = queryset.first()
        model_config.is_active = True
        model_config.save()
        
        self.message_user(request, f"已激活模型配置 '{model_config.name}'")
    activate_model.short_description = "激活所选模型"
    
    def reload_model(self, request, queryset):
        """重新加载所选模型"""
        if queryset.count() > 1:
            self.message_user(request, "一次只能重新加载一个模型配置", level='error')
            return
        
        model_config = queryset.first()
        
        try:
            # 导入模型服务模块
            from core.model_service import reload_model
            
            # 重新加载模型
            result = reload_model(model_config.id)
            
            if result.get('status') == 'success':
                self.message_user(request, f"模型 '{model_config.name}' 重新加载成功")
            else:
                self.message_user(request, f"重新加载模型时出错: {result.get('message')}", level='error')
                
        except Exception as e:
            self.message_user(request, f"重新加载模型时出错: {str(e)}", level='error')
    reload_model.short_description = "重新加载所选模型"
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('模型配置', {
            'fields': ('model_path', 'device', 'precision', 'batch_size')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    """知识分块的管理配置"""
    list_display = ('id', 'knowledge_base', 'content_preview', 'is_indexed_tag', 'created_at')
    list_filter = ('is_indexed', 'knowledge_base', 'created_at')
    search_fields = ('content', 'knowledge_base__name')
    readonly_fields = ('is_indexed', 'created_at')
    
    def content_preview(self, obj):
        """内容预览"""
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return preview
    content_preview.short_description = '内容预览'
    
    def is_indexed_tag(self, obj):
        """将索引状态显示为彩色标签"""
        if obj.is_indexed:
            return format_html('<span style="background-color:#28a745; color:white; padding:2px 8px; border-radius:4px;">已索引</span>')
        else:
            return format_html('<span style="background-color:#dc3545; color:white; padding:2px 8px; border-radius:4px;">未索引</span>')
    is_indexed_tag.short_description = '索引状态'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('knowledge_base',)
        }),
        ('内容', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('索引信息', {
            'fields': ('is_indexed', 'metadata')
        }),
        ('时间信息', {
            'fields': ('created_at',),
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
    
    # 添加提示词编辑器、导入知识库链接和模型服务状态
    app_list.append({
        'name': '工具',
        'app_label': 'tools',
        'models': [{
            'name': '提示词编辑器',
            'object_name': 'prompteditor',
            'admin_url': reverse('management:prompt_editor'),
            'view_only': True,
        }, {
            'name': '导入知识库',
            'object_name': 'importkb',
            'admin_url': reverse('management:import_knowledge_base'),
            'view_only': True,
        }, {
            'name': '向量搜索',
            'object_name': 'vectorsearch',
            'admin_url': reverse('management:vector_search_ui'),
            'view_only': True,
        }, {
            'name': '模型服务状态',
            'object_name': 'modelstatus',
            'admin_url': reverse('management:model_service_status'),
            'view_only': True,
        }]
    })
    
    return app_list

# 替换方法
admin.AdminSite.get_app_list = custom_get_app_list
