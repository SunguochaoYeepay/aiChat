import json
import time
import re
from django.http import JsonResponse
from django.utils import timezone
from django.urls import resolve

from .models import APIEndpoint, APILog, APIKey

class APILoggingMiddleware:
    """
    API调用日志记录中间件
    
    记录所有API请求的详细信息，包括请求参数、响应状态、响应时间等
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # API路径模式，匹配/api/开头的路径或views中定义的原有API路径
        self.api_path_pattern = re.compile(r'^/api/|^/analyze$|^/v1/chat/completions$|^/search$|^/status$')
    
    def __call__(self, request):
        # 判断是否是API请求
        if not self.api_path_pattern.match(request.path):
            return self.get_response(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 尝试解析请求体为JSON
        request_data = {}
        if request.body:
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError:
                # 如果不是有效的JSON，记录原始内容
                request_data = {'raw_content': request.body.decode('utf-8', errors='replace')}
        
        # 获取请求头信息
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 获取API密钥
        api_key = request.META.get('HTTP_X_API_KEY', '')
        
        # 处理请求
        response = self.get_response(request)
        
        # 计算响应时间（毫秒）
        response_time = (time.time() - start_time) * 1000
        
        # 获取响应大小
        response_size = len(response.content) if hasattr(response, 'content') else 0
        
        # 获取或创建API端点记录
        path = request.path
        method = request.method
        
        try:
            # 尝试获取匹配的API端点
            endpoint, created = APIEndpoint.objects.get_or_create(
                path=path,
                method=method,
                defaults={
                    'name': f"{method} {path}",
                    'description': f"自动创建的API端点 ({timezone.now().strftime('%Y-%m-%d %H:%M:%S')})"
                }
            )
            
            # 更新API端点的统计信息
            if 200 <= response.status_code < 300:
                # 成功请求
                new_avg_time = ((endpoint.average_response_time * endpoint.call_count) + response_time) / (endpoint.call_count + 1)
                endpoint.call_count += 1
                endpoint.average_response_time = new_avg_time
            else:
                # 错误请求
                endpoint.error_count += 1
            
            endpoint.save(update_fields=['call_count', 'error_count', 'average_response_time'])
            
            # 创建API调用日志
            APILog.objects.create(
                endpoint=endpoint,
                ip_address=ip_address,
                user_agent=user_agent,
                request_data=request_data,
                status_code=response.status_code,
                response_time=response_time,
                response_size=response_size,
                error_message=self.get_error_message(response) if response.status_code >= 400 else None,
                api_key=api_key,
            )
            
            # 如果使用了API密钥，更新API密钥的调用次数
            if api_key:
                try:
                    key_obj = APIKey.objects.get(key=api_key)
                    key_obj.call_count += 1
                    key_obj.save(update_fields=['call_count'])
                except APIKey.DoesNotExist:
                    pass
                
        except Exception as e:
            # 记录日志中间件不应该影响正常请求处理
            print(f"API日志记录错误: {str(e)}")
        
        return response
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_error_message(self, response):
        """从响应中提取错误信息"""
        if response.status_code < 400:
            return None
            
        try:
            if hasattr(response, 'content'):
                # 尝试解析JSON响应
                data = json.loads(response.content.decode('utf-8'))
                if 'error' in data:
                    return data['error']
                elif 'message' in data:
                    return data['message']
            return f"HTTP错误 {response.status_code}"
        except Exception:
            return f"HTTP错误 {response.status_code}"

class APIKeyMiddleware:
    """
    API密钥验证中间件
    
    验证请求中的API密钥，并强制执行速率限制和IP限制
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # API路径模式，匹配/api/开头的路径或views中定义的原有API路径
        self.api_path_pattern = re.compile(r'^/api/|^/analyze$|^/v1/chat/completions$|^/search$|^/status$')
        
        # 路径白名单，不需要API密钥验证的路径
        self.path_whitelist = [
            '/api/',  # API根路径（索引页面）
            '/api/status',  # 状态检查API
            '/status',  # 原始状态检查API
        ]
    
    def __call__(self, request):
        # 判断是否是API请求
        if not self.api_path_pattern.match(request.path) or request.path in self.path_whitelist:
            return self.get_response(request)
        
        # 获取API密钥
        api_key = request.META.get('HTTP_X_API_KEY', '')
        
        # 如果未提供API密钥
        if not api_key:
            return JsonResponse({
                'error': '未提供API密钥，请在请求头中添加X-API-Key'
            }, status=401)
        
        # 验证API密钥
        try:
            key_obj = APIKey.objects.get(key=api_key)
            
            # 检查密钥是否已激活
            if not key_obj.is_active:
                return JsonResponse({
                    'error': 'API密钥已被禁用'
                }, status=403)
            
            # 检查密钥是否已过期
            if key_obj.is_expired():
                return JsonResponse({
                    'error': 'API密钥已过期'
                }, status=403)
            
            # 检查IP限制
            if key_obj.allowed_ips:
                client_ip = self.get_client_ip(request)
                allowed_ips = [ip.strip() for ip in key_obj.allowed_ips.split(',')]
                if client_ip not in allowed_ips:
                    return JsonResponse({
                        'error': f'此API密钥不允许从IP {client_ip} 访问'
                    }, status=403)
            
            # 检查速率限制（此处仅为示例，真实实现应使用Redis等工具进行速率限制）
            # 在这个简化实现中，我们不检查速率限制
            
        except APIKey.DoesNotExist:
            return JsonResponse({
                'error': '无效的API密钥'
            }, status=401)
        
        # 验证通过，继续处理请求
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """获取客户端真实IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 