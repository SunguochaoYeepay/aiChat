"""
API测试模块 - 测试API接口功能

此模块包含API接口的测试用例。
"""
from django.test import TestCase, Client
from django.urls import reverse
import json

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