from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import APIKey

def api_key_required(view_func):
    """
    验证API密钥的装饰器
    
    如果是Django管理员用户则跳过验证
    如果是API请求则验证密钥
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # 检查是否已登录的Django管理员用户
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # 检查API密钥
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return JsonResponse({
                'status': 'error',
                'message': '未提供API密钥'
            }, status=401)
        
        # 验证API密钥
        try:
            key = APIKey.objects.get(key=api_key, is_active=True)
            # 添加API密钥信息到请求中
            request.api_key = key
            return view_func(request, *args, **kwargs)
        except APIKey.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'API密钥无效'
            }, status=401)
    
    return wrapped_view 