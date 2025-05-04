"""
向量搜索服务模块 - 提供向量搜索功能的简化接口
"""
import logging
from .utils import (
    get_embedding_model, 
    text_to_vector,
    create_vector_index,
    add_document_to_index,
    rebuild_vector_index,
    vector_search,
    import_knowledge_base_to_vector
)
from .models import VectorIndex

logger = logging.getLogger(__name__)

# 默认向量维度
DEFAULT_VECTOR_DIMENSION = 384

def initialize_vector_search():
    """
    初始化向量搜索环境
    """
    try:
        # 加载嵌入模型，这将初始化sentence-transformers
        model = get_embedding_model()
        logger.info(f"成功加载向量嵌入模型，向量维度: {model.get_sentence_embedding_dimension()}")
        
        # 检查知识库索引是否存在，如果不存在则创建
        try:
            kb_index = VectorIndex.objects.get(name="knowledge_base")
            logger.info(f"找到知识库向量索引: {kb_index.name}，包含 {kb_index.document_count} 个文档")
        except VectorIndex.DoesNotExist:
            # 导入知识库内容到向量索引
            try:
                result = import_knowledge_base_to_vector()
                logger.info(f"创建了知识库向量索引，导入了 {result['document_count']} 个文档")
            except Exception as e:
                logger.warning(f"导入知识库内容到向量索引时出错: {str(e)}")
                # 创建空索引
                kb_index = create_vector_index("knowledge_base", "知识库向量索引")
                logger.info(f"创建了空的知识库向量索引: {kb_index.name}")
        
        return True
    except Exception as e:
        logger.exception(f"初始化向量搜索环境时出错: {str(e)}")
        return False

def create_embeddings(texts):
    """
    为文本列表创建向量嵌入
    
    Args:
        texts: 文本列表
        
    Returns:
        list: 向量嵌入列表
    """
    try:
        model = get_embedding_model()
        vectors = model.encode(texts)
        return vectors.tolist()
    except Exception as e:
        logger.exception(f"创建向量嵌入时出错: {str(e)}")
        return None

def search_knowledge_base(query, top_k=5):
    """
    搜索知识库
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
        
    Returns:
        list: 搜索结果列表
    """
    try:
        # 获取知识库索引
        try:
            kb_index = VectorIndex.objects.get(name="knowledge_base")
        except VectorIndex.DoesNotExist:
            logger.warning("知识库向量索引不存在，尝试创建")
            initialize_vector_search()
            try:
                kb_index = VectorIndex.objects.get(name="knowledge_base")
            except VectorIndex.DoesNotExist:
                logger.error("无法创建知识库向量索引")
                return []
        
        # 执行向量搜索
        results = vector_search(kb_index, query, top_k)
        
        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result['document_id'].split('_')[-1],  # 从kb_123中提取123
                'content': result['text'],
                'metadata': result['metadata'],
                'similarity': result['score']
            })
        
        return formatted_results
    except Exception as e:
        logger.exception(f"搜索知识库时出错: {str(e)}")
        return [] 