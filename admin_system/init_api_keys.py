import os
import django
import secrets
import string

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()

from api.models import APIKey

def generate_key():
    """生成一个随机的API密钥"""
    alphabet = string.ascii_letters + string.digits
    # 生成32位随机密钥
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def init_api_keys():
    """初始化API密钥"""
    
    # 定义初始API密钥
    initial_keys = [
        {
            'name': '开发测试密钥',
            'description': '用于开发和测试的API密钥',
            'key': generate_key(),
            'is_active': True,
            'allowed_ips': '127.0.0.1,localhost',  # 本地测试IP
        },
        {
            'name': '前端应用密钥',
            'description': '用于前端应用访问API的密钥',
            'key': generate_key(),
            'is_active': True,
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for key_data in initial_keys:
        # 检查是否已有同名密钥
        exists = APIKey.objects.filter(name=key_data['name']).exists()
        
        if not exists:
            # 创建新的API密钥
            api_key = APIKey(**key_data)
            api_key.save()
            created_count += 1
            print(f"创建API密钥: {api_key.name}")
            print(f"密钥值: {api_key.key}")
        else:
            skipped_count += 1
            print(f"跳过已存在的API密钥: {key_data['name']}")
    
    print(f"\n完成初始化! 创建了 {created_count} 个新API密钥, 跳过了 {skipped_count} 个已存在的API密钥。")

if __name__ == '__main__':
    print("开始初始化API密钥...")
    init_api_keys() 