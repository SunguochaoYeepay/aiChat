"""
WebSocket连接管理器 - 管理WebSocket连接

此模块提供WebSocket连接的管理功能，包括连接、断开、发送消息等操作。
"""
from typing import List, Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer

class ConnectionManager:
    """WebSocket连接管理器类"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, AsyncWebsocketConsumer] = {}
    
    async def connect(self, websocket: AsyncWebsocketConsumer, client_id: str):
        """
        添加新的WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            client_id: 客户端ID
        """
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """
        移除WebSocket连接
        
        Args:
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_text(self, client_id: str, message: str):
        """
        发送文本消息
        
        Args:
            client_id: 客户端ID
            message: 要发送的消息内容
        """
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def send_json(self, client_id: str, data: Dict[str, Any]):
        """
        发送JSON数据
        
        Args:
            client_id: 客户端ID
            data: 要发送的JSON数据
        """
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(data)
    
    async def broadcast(self, message: str):
        """
        广播文本消息给所有连接
        
        Args:
            message: 要广播的消息内容
        """
        for conn in self.active_connections.values():
            await conn.send_text(message)
    
    async def broadcast_json(self, data: Dict[str, Any]):
        """
        广播JSON数据给所有连接
        
        Args:
            data: 要广播的JSON数据
        """
        for conn in self.active_connections.values():
            await conn.send_json(data)
    
    def get_connection_count(self) -> int:
        """
        获取当前连接数
        
        Returns:
            int: 当前连接数
        """
        return len(self.active_connections)

# 创建全局连接管理器实例
manager = ConnectionManager() 