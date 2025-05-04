"""
WebSocket消费者 - 实现与原系统兼容的WebSocket接口

此模块实现了与原有系统兼容的WebSocket接口，支持聊天和图像分析功能。
"""
import json
import asyncio
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer

# 导入核心功能模块
from core.websocket.handlers import handle_chat_message, handle_analyze_message, handle_status_request
from core.websocket.managers import manager

class ChatConsumer(AsyncWebsocketConsumer):
    """聊天WebSocket消费者"""
    
    async def connect(self):
        """处理连接请求"""
        # 生成客户端唯一ID
        self.client_id = str(uuid.uuid4())
        
        # 接受WebSocket连接
        await self.accept()
        
        # 将连接添加到管理器
        await manager.connect(self, self.client_id)
        
        # 发送连接成功消息
        await self.send_json({
            'status': 'connected',
            'client_id': self.client_id
        })
        
    async def disconnect(self, close_code):
        """处理断开连接"""
        # 从管理器中移除连接
        manager.disconnect(self.client_id)
    
    async def receive(self, text_data):
        """接收消息"""
        try:
            # 解析JSON消息
            data = json.loads(text_data)
            
            # 根据消息类型处理
            message_type = data.get('type', 'chat')
            
            if message_type == 'chat':
                # 处理聊天消息
                await handle_chat_message(self.client_id, data)
            elif message_type == 'status':
                # 处理状态请求
                await handle_status_request(self.client_id)
            else:
                # 未知消息类型
                await self.send_json({
                    'status': 'error',
                    'message': f'未知消息类型: {message_type}'
                })
        
        except json.JSONDecodeError:
            # JSON解析错误
            await self.send_json({
                'status': 'error',
                'message': '无效的JSON格式'
            })
            
        except Exception as e:
            # 其他错误
            await self.send_json({
                'status': 'error',
                'message': f'处理消息时出错: {str(e)}'
            })
    
    async def send_text(self, message):
        """发送文本消息"""
        await self.send(text_data=message)
    
    async def send_json(self, content):
        """发送JSON消息"""
        await self.send(text_data=json.dumps(content))

class AnalyzeConsumer(AsyncWebsocketConsumer):
    """图像分析WebSocket消费者"""
    
    async def connect(self):
        """处理连接请求"""
        # 生成客户端唯一ID
        self.client_id = str(uuid.uuid4())
        
        # 接受WebSocket连接
        await self.accept()
        
        # 将连接添加到管理器
        await manager.connect(self, self.client_id)
        
        # 发送连接成功消息
        await self.send_json({
            'status': 'connected',
            'client_id': self.client_id
        })
        
    async def disconnect(self, close_code):
        """处理断开连接"""
        # 从管理器中移除连接
        manager.disconnect(self.client_id)
    
    async def receive(self, text_data):
        """接收消息"""
        try:
            # 解析JSON消息
            data = json.loads(text_data)
            
            # 根据消息类型处理
            message_type = data.get('type', 'analyze')
            
            if message_type == 'analyze':
                # 处理图像分析消息
                await handle_analyze_message(self.client_id, data)
            elif message_type == 'status':
                # 处理状态请求
                await handle_status_request(self.client_id)
            else:
                # 未知消息类型
                await self.send_json({
                    'status': 'error',
                    'message': f'未知消息类型: {message_type}'
                })
        
        except json.JSONDecodeError:
            # JSON解析错误
            await self.send_json({
                'status': 'error',
                'message': '无效的JSON格式'
            })
            
        except Exception as e:
            # 其他错误
            await self.send_json({
                'status': 'error',
                'message': f'处理消息时出错: {str(e)}'
            })
    
    async def send_text(self, message):
        """发送文本消息"""
        await self.send(text_data=message)
    
    async def send_json(self, content):
        """发送JSON消息"""
        await self.send(text_data=json.dumps(content)) 