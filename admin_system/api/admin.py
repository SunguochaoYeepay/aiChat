from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils import timezone
import uuid
import secrets
import string
from .models import APIEndpoint, APILog, APIKey

@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    """API接口的管理配置"""
    list_display = ('name', 'method', 'path', 'version', 'status_tag', 'permission_tag', 'call_count', 'error_count', 'average_response_time', 'operations')
    list_filter = ('method', 'status', 'permission', 'version')
    search_fields = ('name', 'path', 'description')
    readonly_fields = ('call_count', 'error_count', 'average_response_time', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'path', 'method', 'version')
        }),
        ('状态与权限', {
            'fields': ('status', 'permission')
        }),
        ('参数配置', {
            'fields': ('request_schema', 'response_schema'),
            'classes': ('collapse',),
        }),
        ('限制与统计', {
            'fields': ('rate_limit', 'call_count', 'error_count', 'average_response_time')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['reset_statistics']
    
    def reset_statistics(self, request, queryset):
        """重置所选接口的统计数据"""
        rows_updated = queryset.update(call_count=0, error_count=0, average_response_time=0)
        self.message_user(request, f'成功重置 {rows_updated} 个接口的统计数据')
    reset_statistics.short_description = "重置所选接口的统计数据"
    
    def operations(self, obj):
        """添加操作列，包含测试按钮"""
        return format_html(
            '<a href="/api/test/?endpoint_id={}" class="button" target="_blank" style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;">测试</a>',
            obj.id
        )
    operations.short_description = '操作'

@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    """API调用日志的管理配置"""
    list_display = ('endpoint', 'status_tag', 'ip_address', 'response_time', 'user_id', 'created_at')
    list_filter = ('endpoint__name', 'status_code', 'created_at')
    search_fields = ('ip_address', 'user_id', 'api_key', 'error_message')
    readonly_fields = ('endpoint', 'ip_address', 'user_agent', 'request_data', 'status_code', 
                      'response_time', 'response_size', 'error_message', 'user_id', 'api_key', 'created_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('endpoint', 'status_code', 'created_at')
        }),
        ('请求信息', {
            'fields': ('ip_address', 'user_agent', 'user_id', 'api_key')
        }),
        ('数据信息', {
            'fields': ('request_data', 'response_time', 'response_size')
        }),
        ('错误信息', {
            'fields': ('error_message',),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """API密钥的管理配置"""
    list_display = ('name', 'key_preview', 'status_tag', 'call_count', 'expires_at', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'key', 'description')
    readonly_fields = ('key', 'call_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'key')
        }),
        ('状态与权限', {
            'fields': ('is_active', 'expires_at')
        }),
        ('限制', {
            'fields': ('allowed_ips', 'rate_limit_override')
        }),
        ('统计', {
            'fields': ('call_count',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['generate_new_key', 'reset_count', 'deactivate_keys', 'activate_keys']
    
    def key_preview(self, obj):
        """显示密钥的预览，只显示前6位和后4位"""
        if len(obj.key) > 10:
            return f"{obj.key[:6]}...{obj.key[-4:]}"
        return obj.key
    key_preview.short_description = 'API密钥'
    
    def get_readonly_fields(self, request, obj=None):
        """新建时不将key设为只读"""
        if obj:  # 编辑现有对象
            return self.readonly_fields
        return ('call_count', 'created_at', 'updated_at')  # 新建对象
    
    def save_model(self, request, obj, form, change):
        """保存模型时，如果是新建，自动生成密钥"""
        if not change:  # 新建对象
            obj.key = self.generate_key()
        super().save_model(request, obj, form, change)
    
    def generate_key(self):
        """生成新的API密钥"""
        alphabet = string.ascii_letters + string.digits
        # 生成32位随机密钥
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def generate_new_key(self, request, queryset):
        """重新生成所选API密钥"""
        for api_key in queryset:
            api_key.key = self.generate_key()
            api_key.save()
        self.message_user(request, f'成功为 {queryset.count()} 个API密钥生成新密钥')
    generate_new_key.short_description = "重新生成所选API密钥"
    
    def reset_count(self, request, queryset):
        """重置所选API密钥的调用次数"""
        rows_updated = queryset.update(call_count=0)
        self.message_user(request, f'成功重置 {rows_updated} 个API密钥的调用次数')
    reset_count.short_description = "重置所选API密钥的调用次数"
    
    def deactivate_keys(self, request, queryset):
        """禁用所选API密钥"""
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f'成功禁用 {rows_updated} 个API密钥')
    deactivate_keys.short_description = "禁用所选API密钥"
    
    def activate_keys(self, request, queryset):
        """激活所选API密钥"""
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {rows_updated} 个API密钥')
    activate_keys.short_description = "激活所选API密钥" 