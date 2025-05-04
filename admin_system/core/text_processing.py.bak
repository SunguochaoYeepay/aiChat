"""
文本处理模块 - 负责文本生成和对话功能

此模块提供文本对话、聊天历史管理等功能，支持与大模型的文本交互。
"""
import time
from .model_service import get_model

def chat_completion(messages, stream=False):
    """
    生成聊天响应
    
    Args:
        messages: 聊天消息列表
        stream: 是否使用流式响应
    
    Returns:
        dict: 包含响应内容的字典
    """
    try:
        # 获取开始时间
        start_time = time.time()
        
        # 获取模型和tokenizer
        model, tokenizer = get_model()
        
        # 处理历史消息
        history = []
        prompt = ""
        
        if messages:
            # 取最后一条用户消息作为当前查询
            current_msg = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    current_msg = msg.get("content", "")
                    break
            
            if not current_msg:
                return {
                    "error": "未找到用户消息",
                    "processing_time": "N/A"
                }
            
            # 构建历史消息
            for i in range(0, len(messages) - 1, 2):
                if i + 1 < len(messages):
                    if messages[i].get("role") == "user" and messages[i+1].get("role") == "assistant":
                        user_msg = messages[i].get("content", "")
                        ai_msg = messages[i+1].get("content", "")
                        history.append([user_msg, ai_msg])
            
            prompt = current_msg
        else:
            return {
                "error": "消息列表为空",
                "processing_time": "N/A"
            }
        
        # 流式响应处理
        if stream:
            # 这里使用生成器实现流式响应
            def generate_stream():
                response, _ = model.chat(tokenizer, prompt, history=history)
                yield response
                
            return {
                "stream": generate_stream(),
                "processing_time": "流式响应中"
            }
        else:
            # 标准响应
            response, new_history = model.chat(tokenizer, prompt, history=history)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            return {
                "id": f"chatcmpl-{int(time.time()*1000)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "qwen-vl-chat",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,  # 暂不计算具体token
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "processing_time": f"{processing_time:.2f}秒"
            }
    except Exception as e:
        return {
            "error": f"处理过程中出错: {str(e)}",
            "processing_time": "N/A"
        } 