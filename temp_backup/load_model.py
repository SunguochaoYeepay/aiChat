import os
import sys
import traceback

try:
    print("开始执行脚本...")
    # 将项目目录添加到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"Python路径: {sys.path}")
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
    print("Django环境设置完成")
    
    # 导入Django
    import django
    django.setup()
    print("Django初始化完成")
    
    # 导入模型服务模块
    print("正在导入模块...")
    from core.model_service import init_model, get_service_status
    print("模块导入成功")
    
    # 初始化并加载模型
    print("正在加载模型...")
    result = init_model()
    print(f"加载结果: {result}")
    
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
    
    # 打印模型配置（如果有）
    model_config = status.get('model_config', {})
    if model_config:
        print("\n模型配置:")
        print(f"路径: {model_config.get('path', 'unknown')}")
        print(f"设备: {model_config.get('device', 'unknown')}")
        print(f"精度: {model_config.get('precision', 'unknown')}")
        
except Exception as e:
    print(f"出错了: {str(e)}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
print("脚本执行完毕") 