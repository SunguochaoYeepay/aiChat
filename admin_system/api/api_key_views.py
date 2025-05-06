from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import secrets
import string
from datetime import datetime
from .models import APIKey
from .decorators import api_key_required

@api_key_required
def api_keys(request):
    """获取所有API密钥"""
    # 获取所有API密钥信息（移除敏感信息）
    keys = []
    for key in APIKey.objects.all():
        keys.append({
            'id': key.id,
            'name': key.name,
            'key': f"{key.key[:8]}...{key.key[-4:]}",  # 仅显示部分密钥
            'created_at': key.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': key.is_active,
            'call_count': key.call_count,
            'description': key.description,
            'expires_at': key.expires_at.strftime('%Y-%m-%d %H:%M:%S') if key.expires_at else None,
            'allowed_ips': key.allowed_ips,
            'rate_limit_override': key.rate_limit_override
        })
    
    return JsonResponse({'api_keys': keys})

@login_required
@csrf_exempt
def create_api_key(request):
    """创建API密钥"""
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name')
        
        if not name:
            return JsonResponse({'error': '密钥名称不能为空'}, status=400)
        
        # 生成随机API密钥
        api_key = generate_api_key()
        
        # 创建API密钥记录
        key = APIKey(
            name=name,
            key=api_key,
            description=data.get('description', ''),
            is_active=data.get('is_active', True),
            expires_at=parse_datetime(data.get('expires_at')) if data.get('expires_at') else None,
            allowed_ips=data.get('allowed_ips', ''),
            rate_limit_override=data.get('rate_limit_override')
        )
        key.save()
        
        # 返回API密钥信息（包括完整密钥，仅在创建时显示一次）
        return JsonResponse({
            'status': 'success',
            'message': '创建API密钥成功',
            'api_key': api_key,
            'key_info': {
                'id': key.id,
                'name': key.name,
                'created_at': key.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': key.is_active
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': f'创建API密钥失败: {str(e)}'}, status=500)

@login_required
@csrf_exempt
def update_api_key(request, key_id):
    """更新API密钥"""
    if request.method != 'PUT' and request.method != 'PATCH':
        return JsonResponse({'error': '仅支持PUT/PATCH请求'}, status=405)
    
    try:
        # 获取要更新的API密钥
        try:
            key = APIKey.objects.get(id=key_id)
        except APIKey.DoesNotExist:
            return JsonResponse({'error': 'API密钥不存在'}, status=404)
        
        data = json.loads(request.body)
        
        # 更新API密钥信息
        if 'name' in data:
            key.name = data['name']
        
        if 'description' in data:
            key.description = data['description']
        
        if 'is_active' in data:
            key.is_active = data['is_active']
        
        if 'expires_at' in data and data['expires_at']:
            key.expires_at = parse_datetime(data['expires_at'])
        elif 'expires_at' in data and data['expires_at'] is None:
            key.expires_at = None
        
        if 'allowed_ips' in data:
            key.allowed_ips = data['allowed_ips']
        
        if 'rate_limit_override' in data:
            key.rate_limit_override = data['rate_limit_override']
        
        key.save()
        
        return JsonResponse({
            'status': 'success',
            'message': '更新API密钥成功',
            'key_info': {
                'id': key.id,
                'name': key.name,
                'is_active': key.is_active,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': f'更新API密钥失败: {str(e)}'}, status=500)

@login_required
@csrf_exempt
def delete_api_key(request, key_id):
    """删除API密钥"""
    if request.method != 'DELETE':
        return JsonResponse({'error': '仅支持DELETE请求'}, status=405)
    
    try:
        # 获取要删除的API密钥
        try:
            key = APIKey.objects.get(id=key_id)
        except APIKey.DoesNotExist:
            return JsonResponse({'error': 'API密钥不存在'}, status=404)
        
        key_name = key.name
        key.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'API密钥 {key_name} 已删除'
        })
    
    except Exception as e:
        return JsonResponse({'error': f'删除API密钥失败: {str(e)}'}, status=500)

def generate_api_key():
    """生成随机API密钥"""
    # 生成一个64字符的随机字符串作为API密钥
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(64))
    return api_key

def parse_datetime(datetime_str):
    """解析日期时间字符串"""
    try:
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None 