from django.db import models
from django.utils.html import format_html

class APIEndpoint(models.Model):
    """API接口管理模型"""
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    )
    
    STATUS_CHOICES = (
        ('active', '活跃'),
        ('deprecated', '已弃用'),
        ('maintenance', '维护中'),
    )
    
    PERMISSION_CHOICES = (
        ('public', '公开'),
        ('authenticated', '需要认证'),
        ('admin', '仅管理员'),
    )
    
    name = models.CharField('接口名称', max_length=100)
    description = models.TextField('接口描述', blank=True, null=True)
    path = models.CharField('接口路径', max_length=255)
    method = models.CharField('请求方法', max_length=10, choices=METHOD_CHOICES, default='GET')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    permission = models.CharField('权限要求', max_length=20, choices=PERMISSION_CHOICES, default='authenticated')
    
    # 接口参数配置
    request_schema = models.JSONField('请求参数配置', default=dict, blank=True, null=True)
    response_schema = models.JSONField('响应参数配置', default=dict, blank=True, null=True)
    
    # 速率限制配置
    rate_limit = models.IntegerField('速率限制(每分钟)', default=60, help_text='每分钟允许的最大请求次数')
    
    # 统计信息
    call_count = models.IntegerField('调用次数', default=0)
    error_count = models.IntegerField('错误次数', default=0)
    average_response_time = models.FloatField('平均响应时间(毫秒)', default=0)
    
    # 版本控制
    version = models.CharField('版本', max_length=20, default='1.0')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'API接口'
        verbose_name_plural = 'API接口管理'
        ordering = ['path']
        # 确保接口路径和方法的组合是唯一的
        unique_together = ('path', 'method', 'version')
    
    def __str__(self):
        return f"{self.method} {self.path} ({self.version})"
    
    def status_tag(self):
        """将状态显示为彩色标签"""
        colors = {
            'active': '#28a745',  # 绿色
            'deprecated': '#dc3545',  # 红色
            'maintenance': '#ffc107',  # 黄色
        }
        color = colors.get(self.status, '#6c757d')  # 默认灰色
        return format_html('<span style="background-color:{}; color:white; padding:2px 8px; border-radius:4px;">{}</span>',
                         color, self.get_status_display())
    
    def permission_tag(self):
        """将权限要求显示为彩色标签"""
        colors = {
            'public': '#28a745',  # 绿色
            'authenticated': '#007bff',  # 蓝色
            'admin': '#6610f2',  # 紫色
        }
        color = colors.get(self.permission, '#6c757d')  # 默认灰色
        return format_html('<span style="background-color:{}; color:white; padding:2px 8px; border-radius:4px;">{}</span>',
                         color, self.get_permission_display())

class APILog(models.Model):
    """API调用日志"""
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.CASCADE, verbose_name='调用的接口')
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.CharField('用户代理', max_length=500, blank=True, null=True)
    request_data = models.JSONField('请求数据', default=dict, blank=True, null=True)
    
    # 响应信息
    status_code = models.IntegerField('响应状态码')
    response_time = models.FloatField('响应时间(毫秒)')
    response_size = models.IntegerField('响应大小(字节)', default=0)
    
    # 错误信息
    error_message = models.TextField('错误信息', blank=True, null=True)
    
    # 认证信息
    user_id = models.CharField('用户ID', max_length=100, blank=True, null=True)
    api_key = models.CharField('API密钥', max_length=100, blank=True, null=True)
    
    # 时间信息
    created_at = models.DateTimeField('调用时间', auto_now_add=True)
    
    class Meta:
        verbose_name = 'API调用日志'
        verbose_name_plural = 'API调用日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.endpoint} - {self.status_code} - {self.created_at}"
    
    def is_success(self):
        """判断请求是否成功"""
        return 200 <= self.status_code < 300
    
    def status_tag(self):
        """将状态码显示为彩色标签"""
        if 200 <= self.status_code < 300:
            color = '#28a745'  # 绿色，成功
        elif 300 <= self.status_code < 400:
            color = '#17a2b8'  # 蓝绿色，重定向
        elif 400 <= self.status_code < 500:
            color = '#ffc107'  # 黄色，客户端错误
        else:
            color = '#dc3545'  # 红色，服务端错误
        
        return format_html('<span style="background-color:{}; color:white; padding:2px 8px; border-radius:4px;">{}</span>',
                         color, self.status_code)

class APIKey(models.Model):
    """API密钥管理"""
    name = models.CharField('名称', max_length=100)
    key = models.CharField('API密钥', max_length=64, unique=True)
    description = models.TextField('描述', blank=True, null=True)
    
    # 权限控制
    is_active = models.BooleanField('是否激活', default=True)
    expires_at = models.DateTimeField('过期时间', blank=True, null=True)
    
    # 允许的IP地址列表
    allowed_ips = models.TextField('允许的IP地址', blank=True, null=True, 
                                 help_text='多个IP地址请用逗号分隔，留空表示不限制')
    
    # 限制
    rate_limit_override = models.IntegerField('速率限制覆盖', blank=True, null=True,
                                            help_text='每分钟请求数，覆盖接口默认限制，留空表示使用接口默认限制')
    
    # 统计
    call_count = models.IntegerField('调用次数', default=0)
    
    # 时间信息
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'API密钥'
        verbose_name_plural = 'API密钥管理'
    
    def __str__(self):
        return self.name
    
    def is_expired(self):
        """判断密钥是否过期"""
        from django.utils import timezone
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def status_tag(self):
        """将状态显示为彩色标签"""
        if not self.is_active:
            return format_html('<span style="background-color:#dc3545; color:white; padding:2px 8px; border-radius:4px;">已禁用</span>')
        
        if self.is_expired():
            return format_html('<span style="background-color:#ffc107; color:white; padding:2px 8px; border-radius:4px;">已过期</span>')
        
        return format_html('<span style="background-color:#28a745; color:white; padding:2px 8px; border-radius:4px;">激活</span>') 