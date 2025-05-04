"""
设置和测试向量搜索功能
"""
import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # 获取项目根目录和Django项目目录
        root_dir = Path.cwd()
        admin_system_dir = root_dir / "admin_system"
        
        # 添加项目路径到系统路径
        sys.path.append(str(admin_system_dir))
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')
        
        # 初始化Django
        logger.info("初始化Django环境...")
        import django
        django.setup()
        
        # 导入向量搜索模块
        logger.info("导入向量搜索模块...")
        try:
            from vector_search.services import initialize_vector_search, create_embeddings
            
            # 测试句子转换器库
            logger.info("测试sentence-transformers库...")
            import sentence_transformers
            logger.info(f"sentence-transformers 版本: {sentence_transformers.__version__}")
            
            # 测试初始化向量搜索
            logger.info("初始化向量搜索...")
            initialize_vector_search()
            
            # 尝试创建一些示例嵌入
            logger.info("创建示例嵌入...")
            test_texts = [
                "这是一个测试文本，用于生成向量嵌入",
                "向量搜索是信息检索的强大工具",
                "通过语义相似度匹配文档内容"
            ]
            
            embeddings = create_embeddings(test_texts)
            
            if embeddings is not None and len(embeddings) == len(test_texts):
                logger.info(f"成功生成 {len(embeddings)} 个嵌入向量")
                logger.info(f"每个向量维度: {len(embeddings[0])}")
                logger.info("向量搜索功能正常工作")
            else:
                logger.error("生成嵌入向量失败")
                
        except ImportError as e:
            logger.error(f"导入错误: {str(e)}")
            logger.error("请确保已安装 sentence-transformers 库和其他所需依赖")
        except Exception as e:
            logger.exception(f"向量搜索设置过程中出错: {str(e)}")
            
        return True
    except Exception as e:
        logger.exception(f"程序执行出错: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== 向量搜索设置脚本 ===")
    success = main()
    if success:
        logger.info("向量搜索设置完成")
    else:
        logger.error("向量搜索设置失败") 