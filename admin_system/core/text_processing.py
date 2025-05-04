"""
文本处理模块 - 负责文本生成和对话功能

此模块提供文本对话、聊天历史管理等功能，支持与大模型的文本交互。
"""
import time
import logging
from .model_service import get_model

# 设置日志
logger = logging.getLogger(__name__)

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
        
        # 如果模型或tokenizer为None，表示加载失败
        if model is None or tokenizer is None:
            logger.error("无法获取模型或分词器")
            return {
                "error": "模型未正确加载，请检查服务日志",
                "processing_time": "N/A"
            }
        
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
                try:
                    if model is None:
                        yield "模型未加载"
                        return
                    
                    if not hasattr(model, 'chat'):
                        yield "模型不支持chat方法"
                        return
                    
                    response, _ = model.chat(tokenizer, prompt, history=history)
                    yield response
                except Exception as e:
                    logger.exception(f"生成流式响应时出错: {str(e)}")
                    yield f"生成流式响应时出错: {str(e)}"
                
            return {
                "stream": generate_stream(),
                "processing_time": "流式响应中"
            }
        else:
            # 标准响应
            try:
                if model is None:
                    logger.error("模型未加载")
                    return {
                        "error": "模型未加载",
                        "processing_time": "N/A"
                    }
                
                if not hasattr(model, 'chat'):
                    logger.error("模型不支持chat方法")
                    return {
                        "error": "模型不支持chat方法",
                        "processing_time": "N/A"
                    }
                
                logger.info(f"开始生成回复，提示词长度: {len(prompt)}")
                response, new_history = model.chat(tokenizer, prompt, history=history)
                
                # 计算处理时间
                processing_time = time.time() - start_time
                logger.info(f"回复生成完成，耗时: {processing_time:.2f}秒")
                
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
                logger.exception(f"标准响应生成出错: {str(e)}")
                return {
                    "error": f"标准响应生成出错: {str(e)}",
                    "processing_time": "N/A"
                }
    except Exception as e:
        logger.exception(f"处理过程中出错: {str(e)}")
        return {
            "error": f"处理过程中出错: {str(e)}",
            "processing_time": "N/A"
        } 