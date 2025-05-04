"""
WebSocket消息处理器 - 处理WebSocket消息

此模块提供WebSocket消息的处理功能，包括聊天消息和图像分析消息的处理。
"""
import json
import asyncio
import time
from typing import Dict, Any, Optional

# 导入核心功能模块
from ..image_analysis import analyze_image
from ..text_processing import chat_completion
from .managers import manager

async def handle_chat_message(client_id: str, message: Dict[str, Any]):
    """
    处理聊天消息
    
    Args:
        client_id: 客户端ID
        message: 消息内容
    """
    try:
        # 发送处理中状态
        await manager.send_json(client_id, {
            "status": "processing",
            "message": "正在生成回复..."
        })
        
        # 验证消息结构
        if 'messages' not in message:
            await manager.send_json(client_id, {
                "status": "error",
                "message": "消息格式错误，缺少 'messages' 字段"
            })
            return
        
        # 提取聊天消息
        messages = message.get('messages', [])
        
        # 调用聊天完成函数
        result = chat_completion(messages)
        
        # 检查是否有错误
        if 'error' in result:
            await manager.send_json(client_id, {
                "status": "error",
                "message": result['error']
            })
            return
        
        # 发送结果
        await manager.send_json(client_id, {
            "status": "complete",
            "result": result
        })
        
    except Exception as e:
        # 发送错误信息
        await manager.send_json(client_id, {
            "status": "error",
            "message": f"处理消息时出错: {str(e)}"
        })

async def handle_analyze_message(client_id: str, message: Dict[str, Any]):
    """
    处理图像分析消息
    
    Args:
        client_id: 客户端ID
        message: 消息内容
    """
    try:
        # 发送处理中状态
        await manager.send_json(client_id, {
            "status": "processing",
            "message": "正在分析图像..."
        })
        
        # 验证消息结构
        required_fields = ['image_base64', 'query']
        missing_fields = [field for field in required_fields if field not in message]
        
        if missing_fields:
            await manager.send_json(client_id, {
                "status": "error",
                "message": f"消息格式错误，缺少字段: {', '.join(missing_fields)}"
            })
            return
        
        # 提取图像和查询
        image_base64 = message.get('image_base64')
        query = message.get('query')
        
        # 调用图像分析函数
        result = analyze_image(image_base64, query)
        
        # 发送结果
        await manager.send_json(client_id, {
            "status": "complete",
            "result": result.get('result'),
            "processing_time": result.get('processing_time'),
            "boxed_image_url": result.get('boxed_image_url'),
            "boxed_image_urls": result.get('boxed_image_urls')
        })
        
    except Exception as e:
        # 发送错误信息
        await manager.send_json(client_id, {
            "status": "error",
            "message": f"处理图像分析时出错: {str(e)}"
        })

async def handle_status_request(client_id: str):
    """
    处理状态请求
    
    Args:
        client_id: 客户端ID
    """
    try:
        from ..model_service import get_service_status
        
        # 获取服务状态
        status = get_service_status()
        
        # 发送状态信息
        await manager.send_json(client_id, {
            "status": "complete",
            "service_status": status
        })
        
    except Exception as e:
        # 发送错误信息
        await manager.send_json(client_id, {
            "status": "error",
            "message": f"获取状态时出错: {str(e)}"
        }) 