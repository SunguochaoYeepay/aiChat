import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .models import VectorIndex, DocumentVector

# 加载模型，使用全局变量避免重复加载
_model = None

def get_embedding_model():
    """获取嵌入模型，使用单例模式避免重复加载"""
    global _model
    if _model is None:
        try:
            # 使用多语言模型，同时支持中英文
            _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except Exception as e:
            print(f"加载模型出错: {str(e)}")
            # 回退到基础模型
            _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def text_to_vector(text):
    """将文本转换为向量"""
    model = get_embedding_model()
    return model.encode(text)

def create_vector_index(name, description=""):
    """创建向量索引"""
    index = VectorIndex.objects.create(
        name=name,
        description=description,
        document_count=0,
        vector_dimension=get_embedding_model().get_sentence_embedding_dimension()
    )
    return index

def add_document_to_index(index, document_id, text, source="knowledge_base", metadata=None):
    """添加文档到索引"""
    # 创建或更新文档向量
    doc, created = DocumentVector.objects.update_or_create(
        index=index,
        document_id=document_id,
        defaults={
            'source': source,
            'text': text,
            'metadata': metadata or {}
        }
    )
    
    # 更新索引文档数量
    if created:
        index.document_count += 1
        index.save(update_fields=['document_count'])
    
    return doc

def rebuild_vector_index(index):
    """重建向量索引"""
    # 获取所有文档
    documents = DocumentVector.objects.filter(index=index)
    
    if not documents:
        print(f"索引 '{index.name}' 没有文档，跳过重建")
        return
    
    # 提取文本
    texts = [doc.text for doc in documents]
    ids = [doc.id for doc in documents]
    
    # 计算向量嵌入
    model = get_embedding_model()
    vectors = model.encode(texts)
    
    # 保存向量到文件
    vector_file = index.get_vector_file_path()
    np.save(vector_file, vectors)
    
    # 保存元数据
    metadata = {
        "document_ids": ids,
        "document_count": len(documents),
        "vector_dimension": vectors.shape[1]
    }
    
    metadata_file = index.get_metadata_file_path()
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)
    
    # 更新索引信息
    index.document_count = len(documents)
    index.vector_dimension = vectors.shape[1]
    index.save(update_fields=['document_count', 'vector_dimension'])
    
    return True

def get_faiss_index(index):
    """获取FAISS索引"""
    # 加载向量
    vector_file = index.get_vector_file_path()
    if not os.path.exists(vector_file):
        print(f"向量文件不存在: {vector_file}")
        return None
    
    vectors = np.load(vector_file)
    
    # 创建FAISS索引
    dimension = vectors.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)  # L2距离
    faiss_index.add(vectors)
    
    return faiss_index

def vector_search(index, query_text, top_k=5):
    """向量搜索"""
    # 获取FAISS索引
    faiss_index = get_faiss_index(index)
    if faiss_index is None:
        return []
    
    # 加载元数据
    metadata_file = index.get_metadata_file_path()
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # 将查询转换为向量
    query_vector = text_to_vector(query_text)
    query_vector = np.array([query_vector], dtype=np.float32)
    
    # 执行搜索
    distances, indices = faiss_index.search(query_vector, top_k)
    
    # 获取结果
    results = []
    for i, idx in enumerate(indices[0]):
        if idx >= 0 and idx < len(metadata["document_ids"]):
            doc_id = metadata["document_ids"][idx]
            try:
                doc = DocumentVector.objects.get(id=doc_id)
                results.append({
                    "id": doc.id,
                    "document_id": doc.document_id,
                    "source": doc.source,
                    "text": doc.text,
                    "metadata": doc.metadata,
                    "distance": float(distances[0][i]),
                    "score": 1.0 / (1.0 + float(distances[0][i]))  # 将距离转换为相似度分数
                })
            except DocumentVector.DoesNotExist:
                print(f"文档不存在: {doc_id}")
                continue
    
    return results

def import_knowledge_base_to_vector(index_name="knowledge_base"):
    """将知识库导入到向量索引"""
    from management.models import KnowledgeBase
    
    # 获取或创建索引
    index, created = VectorIndex.objects.get_or_create(
        name=index_name,
        defaults={
            'description': '知识库向量索引',
            'vector_dimension': get_embedding_model().get_sentence_embedding_dimension()
        }
    )
    
    # 获取所有知识库文档
    kbs = KnowledgeBase.objects.all()
    
    for kb in kbs:
        # 将知识库添加到向量索引
        add_document_to_index(
            index=index,
            document_id=f"kb_{kb.id}",
            text=kb.content or "",
            source="knowledge_base",
            metadata={
                "name": kb.name,
                "description": kb.description or "",
                "file_path": kb.file_path or ""
            }
        )
    
    # 重建索引
    rebuild_vector_index(index)
    
    return {
        "index": index.name,
        "document_count": index.document_count
    }

def import_prompt_templates_to_vector(index_name="prompt_templates"):
    """将提示词模板导入到向量索引"""
    from management.models import PromptTemplate
    
    # 获取或创建索引
    index, created = VectorIndex.objects.get_or_create(
        name=index_name,
        defaults={
            'description': '提示词模板向量索引',
            'vector_dimension': get_embedding_model().get_sentence_embedding_dimension()
        }
    )
    
    # 获取所有提示词模板
    templates = PromptTemplate.objects.all()
    
    for template in templates:
        # 将提示词模板添加到向量索引
        category, _, type_name = template.name.partition('.')
        
        # 构建搜索文本（组合名称、描述和内容）
        search_text = f"{template.name}\n{template.description or ''}\n{template.content}"
        
        add_document_to_index(
            index=index,
            document_id=f"prompt_{template.id}",
            text=search_text,
            source="prompt_template",
            metadata={
                "name": template.name,
                "category": category,
                "type": type_name,
                "description": template.description or "",
                "content": template.content
            }
        )
    
    # 重建索引
    rebuild_vector_index(index)
    
    return {
        "index": index.name,
        "document_count": index.document_count
    }

def import_all_to_vector(index_name="combined_index"):
    """将知识库和提示词模板都导入到一个统一的向量索引"""
    from management.models import KnowledgeBase, PromptTemplate
    
    # 获取或创建索引
    index, created = VectorIndex.objects.get_or_create(
        name=index_name,
        defaults={
            'description': '知识库和提示词模板的统一向量索引',
            'vector_dimension': get_embedding_model().get_sentence_embedding_dimension()
        }
    )
    
    # 导入知识库
    kbs = KnowledgeBase.objects.all()
    for kb in kbs:
        add_document_to_index(
            index=index,
            document_id=f"kb_{kb.id}",
            text=kb.content or "",
            source="knowledge_base",
            metadata={
                "name": kb.name,
                "description": kb.description or "",
                "file_path": kb.file_path or ""
            }
        )
    
    # 导入提示词模板
    templates = PromptTemplate.objects.all()
    for template in templates:
        category, _, type_name = template.name.partition('.')
        search_text = f"{template.name}\n{template.description or ''}\n{template.content}"
        
        add_document_to_index(
            index=index,
            document_id=f"prompt_{template.id}",
            text=search_text,
            source="prompt_template",
            metadata={
                "name": template.name,
                "category": category,
                "type": type_name,
                "description": template.description or "",
                "content": template.content
            }
        )
    
    # 重建索引
    rebuild_vector_index(index)
    
    return {
        "index": index.name,
        "document_count": index.document_count
    } 