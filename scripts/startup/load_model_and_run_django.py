import os
import sys
import time
import logging
import subprocess
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('model_startup.log')
    ]
)
logger = logging.getLogger(__name__)

# 将项目目录添加到Python路径
current_dir = Path.cwd()
admin_system_dir = current_dir / "admin_system"
sys.path.append(str(admin_system_dir))

# 设置Django环境使用最小化设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')

def wait_for_model_load(timeout=600):
    """
    等待模型加载完成，最多等待指定的超时时间(秒)
    
    Args:
        timeout: 最大等待时间(秒)
        
    Returns:
        bool: 模型是否成功加载
    """
    from core.model_service import get_service_status
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = get_service_status()
        if status['status'] == 'running' and status['model_loaded']:
            return True
        
        if status['status'] == 'error':
            logger.error(f"模型加载失败: {status.get('message', '未知错误')}")
            return False
            
        logger.info(f"等待模型加载... 状态: {status['status']}")
        time.sleep(5)  # 每5秒检查一次
    
    logger.error(f"模型加载超时，已等待{timeout}秒")
    return False

try:
    logger.info("初始化Django...")
    import django
    django.setup()
    logger.info("Django初始化完成")
    
    # 预加载模型
    logger.info("\n预加载模型...")
    from core.model_service import init_model, get_service_status
    
    # 初始化并加载模型
    result = init_model()
    logger.info(f"模型加载启动结果: {result}")
    
    # 等待模型完全加载
    if result['status'] in ['success', 'loading']:
        logger.info("等待模型完全加载...")
        if not wait_for_model_load():
            logger.error("模型未能在规定时间内加载完成，但仍将尝试启动Django")
    else:
        logger.error(f"模型加载失败: {result.get('message', '未知错误')}")
    
    # 获取并打印服务状态
    status = get_service_status()
    logger.info("\n模型服务状态:")
    logger.info(f"状态: {status.get('status', 'unknown')}")
    logger.info(f"消息: {status.get('message', 'unknown')}")
    logger.info(f"模型已加载: {status.get('model_loaded', False)}")
    logger.info(f"GPU可用: {status.get('gpu_available', False)}")
    
    # 打印GPU信息（如果有）
    gpu_info = status.get('gpu_info', {})
    if gpu_info:
        logger.info("\nGPU信息:")
        logger.info(f"名称: {gpu_info.get('name', 'unknown')}")
        logger.info(f"总内存: {gpu_info.get('total_memory', 0):.2f} GB")
        logger.info(f"已分配内存: {gpu_info.get('allocated_memory', 0):.2f} GB")
        logger.info(f"缓存内存: {gpu_info.get('cached_memory', 0):.2f} GB")

    # 进行简单的模型测试
    logger.info("\n执行简单的模型测试...")
    try:
        from core.wrappers.model_wrapper import ModelWrapper
        from core.model_service import get_model
        
        model, tokenizer = get_model()
        if model is None or tokenizer is None:
            logger.error("模型或分词器为空，无法进行测试")
        else:
            response, _ = model.chat(tokenizer, "你好", history=[])
            logger.info(f"测试响应: {response[:100]}...")
            logger.info("模型测试完成")
    except Exception as e:
        logger.exception(f"模型测试失败: {str(e)}")

    # 启动Django
    logger.info("\n启动Django服务器...")
    os.chdir(str(admin_system_dir))
    
    # 使用最小化设置启动Django
    django_cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000", 
                 "--settings=admin_system.minimal_settings"]
    
    subprocess.call(django_cmd)
    
except Exception as e:
    logger.exception(f"启动过程中出错: {str(e)}") 