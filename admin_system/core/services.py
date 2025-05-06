from django.conf import settings
import time
import logging
from functools import wraps
from .model_manager import model_manager
from management.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

def timing_decorator(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"函数 {func.__name__} 耗时 {end_time - start_time:.4f} 秒")
        return result
    return wrapper

@timing_decorator
def chat_completion(messages, stream=False, template_type='general', knowledge_content=''):
    """
    聊天完成服务
    
    Args:
        messages: 消息列表
        stream: 是否流式输出
        template_type: 提示词模板类型
        knowledge_content: 知识库内容
    
    Returns:
        聊天完成结果
    """
    try:
        # 获取模型
        model = model_manager.get_model()
        
        # 处理历史对话
        history = []
        query = ""
        
        # 提取最后一条用户消息作为查询
        for i, msg in enumerate(messages):
            if msg['role'] == 'user' and i == len(messages) - 1:
                query = msg['content']
            elif i > 0:  # 跳过第一条系统消息
                history.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # 获取提示词模板
        template_category = 'chat'
        if knowledge_content:
            template_category = 'search'  # 如果有知识内容，使用搜索模板
            
        template = prompt_manager.get_template(f"{template_category}.{template_type}")
        
        # 如果找不到指定模板，使用通用模板
        if not template:
            template = prompt_manager.get_template(f"{template_category}.general")
        
        # 将历史对话格式化为字符串
        history_str = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in history
        ])
        
        # 替换模板变量
        if template_category == 'chat':
            formatted_prompt = template.format(
                query=query,
                history=history_str
            )
        else:  # 搜索模板
            formatted_prompt = template.format(
                query=query,
                content=knowledge_content
            )
        
        # 构建系统提示词
        system_message = {
            'role': 'system',
            'content': formatted_prompt
        }
        
        # 重建消息列表，添加系统提示词
        new_messages = [system_message]
        for msg in messages:
            if msg['role'] != 'system':  # 跳过原有系统消息
                new_messages.append(msg)
        
        # 调用模型生成回复
        if stream:
            response_generator = model.chat_stream(new_messages)
            return {'stream': response_generator}
        else:
            response = model.chat(new_messages)
            
            return {
                'id': f"chatcmpl-{int(time.time()*1000)}",
                'object': 'chat.completion',
                'created': int(time.time()),
                'model': model.model_name,
                'choices': [
                    {
                        'index': 0,
                        'message': {
                            'role': 'assistant',
                            'content': response
                        },
                        'finish_reason': 'stop'
                    }
                ]
            }
    
    except Exception as e:
        logger.error(f"聊天完成服务出错: {str(e)}")
        raise 