from django.test import TestCase
import numpy as np
import os
import json
from django.conf import settings
from .models import VectorIndex, DocumentVector
from .utils import (
    text_to_vector, 
    create_vector_index, 
    add_document_to_index, 
    rebuild_vector_index,
    vector_search
)

class VectorSearchTests(TestCase):
    """向量搜索功能测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试索引
        self.index = create_vector_index("test_index", "测试索引")
        
        # 添加测试文档
        self.doc1 = add_document_to_index(
            index=self.index,
            document_id="doc1",
            text="北京是中国的首都，拥有悠久的历史和丰富的文化遗产。",
            source="test",
            metadata={"title": "北京简介"}
        )
        
        self.doc2 = add_document_to_index(
            index=self.index,
            document_id="doc2",
            text="上海是中国最大的城市，是重要的经济、金融、贸易和航运中心。",
            source="test",
            metadata={"title": "上海简介"}
        )
        
        self.doc3 = add_document_to_index(
            index=self.index,
            document_id="doc3",
            text="设计师需要注意网页的色彩搭配和布局结构，确保用户体验良好。",
            source="test",
            metadata={"title": "设计规范"}
        )
        
        # 重建索引
        rebuild_vector_index(self.index)
    
    def test_vector_index_creation(self):
        """测试向量索引创建"""
        self.assertEqual(self.index.name, "test_index")
        self.assertEqual(self.index.description, "测试索引")
        self.assertEqual(self.index.document_count, 3)
        
        # 检查索引文件是否存在
        vector_file = self.index.get_vector_file_path()
        metadata_file = self.index.get_metadata_file_path()
        
        self.assertTrue(os.path.exists(vector_file))
        self.assertTrue(os.path.exists(metadata_file))
        
        # 检查元数据
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["document_count"], 3)
    
    def test_vector_search(self):
        """测试向量搜索功能"""
        # 搜索关于城市的信息
        results = vector_search(self.index, "中国城市", top_k=2)
        
        # 验证结果数量
        self.assertEqual(len(results), 2)
        
        # 验证北京或上海在结果中
        found_beijing = False
        found_shanghai = False
        
        for result in results:
            if "北京" in result["text"]:
                found_beijing = True
            if "上海" in result["text"]:
                found_shanghai = True
        
        # 至少有一个城市应该被找到
        self.assertTrue(found_beijing or found_shanghai)
        
        # 搜索设计相关内容
        design_results = vector_search(self.index, "网页设计", top_k=1)
        
        # 验证找到了设计相关内容
        self.assertEqual(len(design_results), 1)
        self.assertIn("设计", design_results[0]["text"])
    
    def test_search_relevance(self):
        """测试搜索结果的相关性"""
        # 搜索北京相关内容
        beijing_results = vector_search(self.index, "北京历史文化", top_k=3)
        
        # 验证最相关的结果是关于北京的
        self.assertIn("北京", beijing_results[0]["text"])
        
        # 搜索上海相关内容
        shanghai_results = vector_search(self.index, "上海经济金融", top_k=3)
        
        # 验证最相关的结果是关于上海的
        self.assertIn("上海", shanghai_results[0]["text"])
    
    def tearDown(self):
        """清理测试环境"""
        # 删除测试索引文件
        vector_file = self.index.get_vector_file_path()
        metadata_file = self.index.get_metadata_file_path()
        
        if os.path.exists(vector_file):
            os.remove(vector_file)
        
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        
        # 删除测试数据
        self.index.delete()
