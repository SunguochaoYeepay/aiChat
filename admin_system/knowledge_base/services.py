"""
知识库服务模块 - 提供知识库向量化和搜索功能

此模块提供文本向量化、知识库分块、向量检索等核心功能。
"""
import os
import numpy as np
import pickle
import re
from django.conf import settings
from management.models import KnowledgeBase, KnowledgeChunk

# 尝试导入向量化所需的库
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("警告: sentence_transformers 库未安装，将使用模拟的向量化功能")

# 本地保存的向量模型
LOCAL_EMBEDDING_MODEL = getattr(settings, 'LOCAL_EMBEDDING_MODEL', 'text2vec-base-chinese')

class VectorService:
    """知识库向量化服务"""
    
    def __init__(self):
        """初始化向量服务"""
        self.model = None
        self.model_name = LOCAL_EMBEDDING_MODEL
    
    def _load_model(self):
        """加载向量模型"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return False
            
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name)
                print(f"成功加载向量模型: {self.model_name}")
                return True
            except Exception as e:
                print(f"加载向量模型失败: {e}")
                return False
        return True
    
    def create_embeddings(self, texts):
        """
        为文本创建向量嵌入
        
        Args:
            texts: 文本列表
            
        Returns:
            numpy.ndarray: 向量数组，如果创建失败则返回None
        """
        if not self._load_model():
            # 如果模型不可用，返回随机向量（仅用于测试）
            return np.random.rand(len(texts), 384).astype(np.float32)
            
        try:
            # 使用模型创建嵌入
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            print(f"创建嵌入时出错: {e}")
            return None
    
    def search_by_vector(self, query_vector, vectors, top_k=5):
        """
        根据向量相似度搜索
        
        Args:
            query_vector: 查询向量
            vectors: 向量列表
            top_k: 返回结果数量
            
        Returns:
            list: 包含 (索引, 相似度) 的元组列表
        """
        if len(vectors) == 0:
            return []
            
        # 计算余弦相似度
        similarities = np.dot(vectors, query_vector) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector)
        )
        
        # 获取前K个最相似的索引
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # 返回 (索引, 相似度) 的列表
        return [(idx, float(similarities[idx])) for idx in top_indices]

# 创建向量服务实例
vector_service = VectorService()

def chunk_text(text, chunk_size=500, overlap=50):
    """
    将文本分割成大小相近的块
    
    Args:
        text: 要分割的文本
        chunk_size: 每个块的大致字符数
        overlap: 块之间的重叠字符数
        
    Returns:
        list: 文本块列表
    """
    # 清理文本
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 如果文本小于块大小，直接返回
    if len(text) <= chunk_size:
        return [text]
    
    # 按段落分割
    paragraphs = re.split(r'\n+', text)
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # 如果段落加上当前块超过了块大小，保存当前块
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            # 保留一部分重叠内容
            current_chunk = current_chunk[-overlap:] if overlap > 0 else ""
        
        current_chunk += para + "\n"
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_knowledge_base(kb_id):
    """
    处理知识库，分块并创建向量
    
    Args:
        kb_id: 知识库ID
        
    Returns:
        bool: 处理是否成功
    """
    try:
        # 获取知识库
        kb = KnowledgeBase.objects.get(id=kb_id)
        
        # 清除现有分块
        kb.knowledgechunk_set.all().delete()
        
        # 分块文本
        text_chunks = chunk_text(kb.content)
        
        # 创建分块记录
        for chunk_content in text_chunks:
            KnowledgeChunk.objects.create(
                knowledge_base=kb,
                content=chunk_content,
                metadata={"source": kb.name}
            )
        
        # 更新文档计数
        kb.update_document_count()
        
        # 对分块进行向量化
        index_knowledge_chunks(kb)
        
        return True
    except Exception as e:
        print(f"处理知识库时出错: {str(e)}")
        return False

def index_knowledge_chunks(kb):
    """
    为知识库的分块创建向量索引
    
    Args:
        kb: 知识库对象
        
    Returns:
        bool: 索引是否成功
    """
    try:
        # 获取未索引的分块
        chunks = kb.chunks.filter(is_indexed=False)
        
        if not chunks.exists():
            print(f"知识库 {kb.name} 没有未索引的分块")
            return True
        
        # 提取分块内容
        texts = [chunk.content for chunk in chunks]
        
        # 创建向量嵌入
        embeddings = vector_service.create_embeddings(texts)
        
        if embeddings is None:
            print(f"为知识库 {kb.name} 创建嵌入失败")
            return False
        
        # 保存向量数据
        for i, chunk in enumerate(chunks):
            # 将numpy数组转换为二进制
            vector_bytes = pickle.dumps(embeddings[i])
            chunk.vector_data = vector_bytes
            chunk.is_indexed = True
            chunk.save(update_fields=['vector_data', 'is_indexed'])
        
        # 更新知识库索引状态
        kb.is_indexed = True
        kb.save(update_fields=['is_indexed'])
        
        print(f"知识库 {kb.name} 向量索引完成，共 {len(chunks)} 个分块")
        return True
    except Exception as e:
        print(f"索引知识库分块时出错: {e}")
        return False

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
        # 获取查询向量
        query_embedding = vector_service.create_embeddings([query])[0]
        
        # 获取所有已索引的分块
        indexed_chunks = KnowledgeChunk.objects.filter(is_indexed=True)
        
        # 如果没有索引的分块，返回空结果
        if not indexed_chunks.exists():
            return []
        
        # 获取分块ID和向量
        chunk_ids = []
        vectors = []
        
        for chunk in indexed_chunks:
            chunk_ids.append(chunk.id)
            vector = pickle.loads(chunk.vector_data)
            vectors.append(vector)
        
        # 将向量列表转换为numpy数组
        vectors = np.array(vectors)
        
        # 搜索相似向量
        results = vector_service.search_by_vector(query_embedding, vectors, top_k)
        
        # 构建结果列表
        search_results = []
        for idx, similarity in results:
            if idx < len(chunk_ids):
                chunk_id = chunk_ids[idx]
                chunk = KnowledgeChunk.objects.get(id=chunk_id)
                search_results.append({
                    'id': chunk.id,
                    'content': chunk.content,
                    'similarity': similarity,
                    'knowledge_base': {
                        'id': chunk.knowledge_base.id,
                        'name': chunk.knowledge_base.name
                    }
                })
        
        return search_results
    except Exception as e:
        print(f"搜索知识库时出错: {e}")
        return [] 