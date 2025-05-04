import os
import sys
import time
import subprocess
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("\n" + "=" * 80)
    print("       Qwen-VL-Chat API 服务启动程序")
    print("=" * 80)
    print("此程序将预加载Qwen-VL-Chat模型并启动API服务\n")

def setup_environment():
    """设置环境"""
    # 获取当前目录
    current_dir = Path.cwd()
    admin_system_dir = current_dir / "admin_system"
    
    # 将项目目录添加到Python路径
    sys.path.append(str(admin_system_dir))
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')
    return current_dir, admin_system_dir

def init_django():
    """初始化Django"""
    try:
        print("\n初始化Django...")
        import django
        django.setup()
        print("Django初始化完成")
        return True
    except Exception as e:
        print(f"Django初始化失败: {str(e)}")
        return False

def load_model():
    """加载模型"""
    try:
        print("\n预加载模型...")
        # 导入模型服务模块
        from core.model_service import init_model, get_service_status
        
        # 直接指定模型路径进行初始化
        model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
        device = "cuda"
        precision = "float16"
        
        print(f"使用以下配置加载模型:")
        print(f"路径: {model_path}")
        print(f"设备: {device}")
        print(f"精度: {precision}")
        
        # 初始化并加载模型
        result = init_model(model_path, device, precision)
        
        if result.get('status') == 'success':
            print(f"\n模型加载成功，耗时: {result.get('message', '').split('耗时:')[-1].strip()}")
            
            # 获取并打印服务状态
            status = get_service_status()
            print("\n模型服务状态:")
            print(f"状态: {status.get('status', 'unknown')}")
            print(f"GPU可用: {status.get('gpu_available', False)}")
            
            # 打印GPU信息（如果有）
            gpu_info = status.get('gpu_info', {})
            if gpu_info:
                print("\nGPU信息:")
                print(f"名称: {gpu_info.get('name', 'unknown')}")
                print(f"总内存: {gpu_info.get('total_memory', 0):.2f} GB")
                print(f"已分配内存: {gpu_info.get('allocated_memory', 0):.2f} GB")
            
            return True
        else:
            print(f"\n模型加载失败: {result.get('message', '')}")
            return False
    
    except Exception as e:
        print(f"模型加载过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def start_server(admin_system_dir):
    """启动Django服务器"""
    try:
        print("\n正在启动API服务器...")
        os.chdir(str(admin_system_dir))
        
        # 使用最小化设置启动Django
        subprocess.call([
            sys.executable, 
            "manage.py", 
            "runserver", 
            "0.0.0.0:8000", 
            "--settings=admin_system.minimal_settings"
        ])
        
        return True
    
    except Exception as e:
        print(f"启动服务器时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 设置环境
    current_dir, admin_system_dir = setup_environment()
    
    # 初始化Django
    if not init_django():
        print("初始化失败，程序退出")
        return
    
    # 加载模型
    if not load_model():
        print("模型加载失败，程序退出")
        return
    
    # 显示成功消息，并指导用户如何使用API
    print("\n" + "=" * 80)
    print("模型已成功加载！现在启动API服务器...")
    print("=" * 80)
    print("API将在以下地址可用:")
    print("- 聊天API: http://localhost:8000/api/v1/chat/completions")
    print("\n使用方法示例:")
    print("""
curl -X POST http://localhost:8000/api/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{
    "messages": [
      {"role": "system", "content": "你是一个有用的助手。"},
      {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
  }'
""")
    print("=" * 80)
    print("按Ctrl+C停止服务器\n")
    
    # 启动服务器
    start_server(admin_system_dir)

if __name__ == "__main__":
    main() 