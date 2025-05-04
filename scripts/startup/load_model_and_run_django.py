import os
import sys
import time
import subprocess
from pathlib import Path

# 将项目目录添加到Python路径
current_dir = Path.cwd()
admin_system_dir = current_dir / "admin_system"
sys.path.append(str(admin_system_dir))

# 设置Django环境使用最小化设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')

try:
    print("初始化Django...")
    import django
    django.setup()
    print("Django初始化完成")
    
    # 预加载模型
    print("\n预加载模型...")
    from core.model_service import init_model, get_service_status
    
    # 初始化并加载模型
    result = init_model()
    print(f"模型加载结果: {result}")
    
    # 获取并打印服务状态
    status = get_service_status()
    print("\n模型服务状态:")
    print(f"状态: {status.get('status', 'unknown')}")
    print(f"消息: {status.get('message', 'unknown')}")
    print(f"模型已加载: {status.get('model_loaded', False)}")
    print(f"GPU可用: {status.get('gpu_available', False)}")
    
    # 打印GPU信息（如果有）
    gpu_info = status.get('gpu_info', {})
    if gpu_info:
        print("\nGPU信息:")
        print(f"名称: {gpu_info.get('name', 'unknown')}")
        print(f"总内存: {gpu_info.get('total_memory', 0):.2f} GB")
        print(f"已分配内存: {gpu_info.get('allocated_memory', 0):.2f} GB")
        print(f"缓存内存: {gpu_info.get('cached_memory', 0):.2f} GB")

    # 启动Django
    print("\n启动Django服务器...")
    os.chdir(str(admin_system_dir))
    
    # 使用最小化设置启动Django
    django_cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000", 
                 "--settings=admin_system.minimal_settings"]
    
    subprocess.call(django_cmd)
    
except Exception as e:
    print(f"启动过程中出错: {str(e)}")
    import traceback
    traceback.print_exc() 