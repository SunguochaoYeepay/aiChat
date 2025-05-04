"""
修复API服务启动问题的简化脚本
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_vector_search():
    """初始化向量搜索功能"""
    logger.info("正在初始化向量搜索功能...")
    try:
        from vector_search.services import initialize_vector_search as init_vs
        result = init_vs()
        if result:
            logger.info("向量搜索功能初始化成功")
        else:
            logger.warning("向量搜索功能初始化失败，但系统将继续启动")
    except ImportError:
        logger.warning("找不到向量搜索模块，确保已安装sentence-transformers和faiss-cpu")
    except Exception as e:
        logger.exception(f"初始化向量搜索时出错: {str(e)}")

def main():
    try:
        # 获取项目根目录和Django项目目录
        root_dir = Path.cwd()
        admin_system_dir = root_dir / "admin_system"
        
        if not admin_system_dir.exists():
            logger.error(f"Django项目目录不存在: {admin_system_dir}")
            return False
            
        # 切换到Django项目目录
        os.chdir(str(admin_system_dir))
        logger.info(f"已切换到Django项目目录: {admin_system_dir}")
        
        # 添加项目路径到Python路径
        sys.path.insert(0, str(admin_system_dir.parent))  # 添加项目根目录
        sys.path.insert(0, str(admin_system_dir))  # 添加Django项目目录
        
        # 设置环境变量
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')
        
        # 运行数据库迁移
        logger.info("正在运行数据库迁移...")
        migrate_cmd = [sys.executable, "manage.py", "migrate", "--settings=admin_system.minimal_settings"]
        result = subprocess.run(migrate_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"数据库迁移失败: {result.stderr}")
        else:
            logger.info("数据库迁移成功")
        
        # 检查模型路径
        model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
        if not os.path.exists(model_path):
            logger.warning(f"模型路径不存在: {model_path}")
            logger.warning("请确保模型已下载到正确位置")
        else:
            logger.info(f"模型路径有效: {model_path}")
        
        # 初始化Django
        try:
            import django
            django.setup()
            logger.info("Django环境初始化成功")
            
            # 初始化向量搜索
            initialize_vector_search()
        except Exception as e:
            logger.exception(f"初始化Django环境时出错: {str(e)}")
            logger.warning("跳过向量搜索初始化，继续启动服务...")
        
        # 启动Django服务
        logger.info("启动API服务...")
        django_cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000", 
                     "--settings=admin_system.minimal_settings"]
        
        subprocess.call(django_cmd)
        return True
        
    except Exception as e:
        logger.exception(f"启动过程中出错: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== API服务修复启动脚本 ===")
    main() 