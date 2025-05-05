"""
Qwen-VL-Chat 模型预加载脚本

此脚本用于在启动API服务前预加载模型，提高首次请求的响应速度。
可独立运行，也可由启动脚本调用。
"""
import os
import sys
import time
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("开始预加载模型...")
    
    # 获取当前目录
    current_dir = Path.cwd()
    admin_system_dir = current_dir / "admin_system"
    
    # 将项目目录添加到Python路径
    sys.path.append(str(admin_system_dir))
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')
    
    logger.info("初始化Django环境...")
    
    try:
        import django
        django.setup()
        logger.info("Django环境初始化成功")
    except Exception as e:
        logger.error(f"Django环境初始化失败: {e}")
        return
    
    # 加载模型
    logger.info("开始加载模型...")
    
    try:
        # 导入模型服务
        from core.model_service import init_model, get_service_status
        
        # 获取默认模型配置
        model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"  # 默认路径
        device = "cuda"  # 默认设备
        precision = "float16"  # 默认精度
        
        logger.info(f"使用以下配置加载模型:")
        logger.info(f"路径: {model_path}")
        logger.info(f"设备: {device}")
        logger.info(f"精度: {precision}")
        
        # 加载模型
        load_start = time.time()
        result = init_model(model_path, device, precision)
        
        if result.get('status') == 'success':
            load_time = time.time() - load_start
            logger.info(f"模型加载成功，耗时: {load_time:.2f}秒")
            
            # 获取并显示服务状态
            status = get_service_status()
            logger.info(f"模型服务状态: {status.get('status', 'unknown')}")
            logger.info(f"GPU可用: {status.get('gpu_available', False)}")
            
            # 输出服务可用信息
            logger.info("\n===================================")
            logger.info("模型加载完成，服务已就绪!")
            logger.info("API服务地址: http://localhost:8000/api/v1/chat/completions")
            logger.info("服务状态查询: http://localhost:8000/api/status")
            logger.info("===================================\n")
            
            # 保持脚本运行以维持模型加载状态
            logger.info("模型加载进程将保持运行...")
            while True:
                time.sleep(60)
                
        else:
            logger.error(f"模型加载失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        logger.exception(f"模型加载过程中出错: {e}")

if __name__ == "__main__":
    main() 