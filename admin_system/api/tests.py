"""
API测试模块 - 测试API接口功能

此模块包含API接口的测试用例。
"""
from django.test import TestCase, Client
from django.urls import reverse
import json
from management.models import KnowledgeBase, KnowledgeChunk
from knowledge_base.services import VectorService
import pickle

class ApiTest(TestCase):
    """API测试类"""
    
    def setUp(self):
        """测试准备工作"""
        self.client = Client()
    
    def test_service_status(self):
        """测试服务状态接口"""
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)
        # 验证返回的JSON结构
        data = json.loads(response.content)
        self.assertIn('status', data)
    
    def test_search_knowledge_base(self):
        """测试知识库搜索接口"""
        response = self.client.post(
            '/search',
            json.dumps({'query': '测试'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        # 验证返回的JSON结构
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertIn('count', data)

# 注意：由于图像分析和聊天完成接口需要模型加载，
# 这里不包含这些测试，应在实际部署环境中手动测试 

class ApiVectorIntegrationTests(TestCase):
    """API与向量检索集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        
        # 创建向量服务
        self.vector_service = VectorService()
        
        # 创建测试知识库
        self.kb1 = KnowledgeBase.objects.create(
            name="测试知识库1",
            description="测试用知识库",
            content="北京是中国的首都，有着丰富的历史文化和现代化设施。天安门、故宫、长城等是著名的旅游景点。"
        )
        
        self.kb2 = KnowledgeBase.objects.create(
            name="测试知识库2",
            description="测试用知识库",
            content="上海是中国最大的城市和全球重要的金融中心。外滩、东方明珠、豫园是著名的旅游景点。"
        )
        
        self.kb3 = KnowledgeBase.objects.create(
            name="设计规范",
            description="网页设计规范",
            content="网页设计应遵循简洁、直观、一致的原则。色彩搭配要协调，布局要合理，交互要流畅。"
        )
        
        # 为知识库创建分块
        for kb in [self.kb1, self.kb2, self.kb3]:
            chunk = KnowledgeChunk.objects.create(
                knowledge_base=kb,
                content=kb.content,
                metadata={"source": kb.name}
            )
            
            # 创建向量
            vector = self.vector_service.create_embeddings([chunk.content])[0]
            chunk.vector_data = pickle.dumps(vector)
            chunk.is_indexed = True
            chunk.save()
            
            # 更新知识库状态
            kb.is_indexed = True
            kb.save()
    
    def test_search_knowledge_base(self):
        """测试知识库搜索API"""
        search_url = reverse('search_knowledge_base')
        
        # 测试北京相关搜索
        data = {
            'query': '北京旅游景点',
            'top_k': 1
        }
        
        response = self.client.post(
            search_url, 
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        # 验证结果包含北京相关内容
        self.assertTrue(len(result['results']) > 0)
        self.assertIn('北京', result['results'][0]['content'])
        
        # 测试设计相关搜索
        data = {
            'query': '网页设计原则',
            'top_k': 1
        }
        
        response = self.client.post(
            search_url, 
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        # 验证结果包含设计相关内容
        self.assertTrue(len(result['results']) > 0)
        self.assertIn('设计', result['results'][0]['content'])
    
    def test_chat_with_knowledge_base(self):
        """测试聊天API是否使用知识库"""
        # 测试相关的查询应返回知识库中的信息
        chat_url = reverse('chat_completions')
        
        # 构造一个查询北京的聊天请求
        data = {
            'messages': [
                {'role': 'user', 'content': '北京有哪些著名的旅游景点？'}
            ]
        }
        
        response = self.client.post(
            chat_url, 
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        # 验证模型回复中包含知识库中的相关信息
        # 注意：这个测试依赖于模型的行为，可能需要调整
        self.assertIn('choices', result)
        self.assertTrue(len(result['choices']) > 0)
        
        content = result['choices'][0]['message']['content']
        
        # 验证回复中包含知识库中的关键信息
        # 至少应该提到天安门、故宫或长城中的一个
        mentioned_landmarks = any(landmark in content for landmark in ['天安门', '故宫', '长城'])
        self.assertTrue(mentioned_landmarks, f"回复中未包含知识库中的地标信息: {content}") 