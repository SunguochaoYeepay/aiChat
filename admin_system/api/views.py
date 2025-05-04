"""
API视图函数 - 提供与原系统兼容的API接口

此模块实现了与原有FastAPI系统兼容的HTTP API接口，确保现有前端能继续正常工作。
"""
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 导入核心功能模块
from core.image_analysis import analyze_image as analyze_image_core
from core.text_processing import chat_completion
from core.model_service import get_service_status as get_model_status
from management.models import KnowledgeBase
from knowledge_base.services import search_knowledge_base as kb_vector_search

@csrf_exempt
@require_http_methods(["POST"])
def analyze_image(request):
    """
    图像分析接口
    
    与原有/analyze接口兼容
    """
    try:
        # 解析JSON请求体
        data = json.loads(request.body)
        
        # 提取图像和查询
        image_base64 = data.get('image_base64')
        query = data.get('query')
        
        # 验证必要字段
        if not image_base64:
            return JsonResponse({
                'error': '缺少图像数据 (image_base64)'
            }, status=400)
            
        if not query:
            return JsonResponse({
                'error': '缺少查询文本 (query)'
            }, status=400)
        
        # 调用核心分析函数
        result = analyze_image_core(image_base64, query)
        
        # 返回结果
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '无效的JSON格式'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'error': f'处理请求时出错: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chat_completions(request):
    """
    聊天完成接口
    
    与原有/v1/chat/completions接口兼容
    """
    try:
        # 解析JSON请求体
        data = json.loads(request.body)
        
        # 提取消息
        messages = data.get('messages', [])
        stream = data.get('stream', False)
        
        # 验证必要字段
        if not messages:
            return JsonResponse({
                'error': '缺少消息列表 (messages)'
            }, status=400)
        
        # 调用核心聊天完成函数
        result = chat_completion(messages, stream)
        
        # 处理流式响应（这里简化处理，实际应使用StreamingHttpResponse）
        if stream and 'stream' in result:
            # 将生成器转换为列表
            responses = list(result['stream'])
            result = {
                'id': f"chatcmpl-{int(time.time()*1000)}",
                'object': 'chat.completion.chunk',
                'choices': [
                    {
                        'index': 0,
                        'delta': {
                            'content': ''.join(responses)
                        },
                        'finish_reason': 'stop'
                    }
                ]
            }
        
        # 返回结果
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '无效的JSON格式'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'error': f'处理请求时出错: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def search_knowledge_base(request):
    """
    知识库搜索接口
    
    与原有/search接口兼容
    """
    try:
        # 解析JSON请求体
        data = json.loads(request.body)
        
        # 提取查询
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        # 验证必要字段
        if not query:
            return JsonResponse({
                'error': '缺少查询文本 (query)'
            }, status=400)
        
        # 使用向量搜索
        vector_results = kb_vector_search(query, top_k)
        
        # 如果向量搜索返回结果，使用这些结果
        if vector_results:
            results = []
            for item in vector_results:
                results.append({
                    'id': item['knowledge_base']['id'],
                    'name': item['knowledge_base']['name'],
                    'content': item['content'],
                    'similarity': item['similarity']
                })
        else:
            # 向量搜索无结果，回退到简单文本搜索
            results = []
            for kb in KnowledgeBase.objects.all():
                if query.lower() in kb.content.lower():
                    # 找到了匹配
                    results.append({
                        'id': kb.id,
                        'name': kb.name,
                        'content': kb.content[:200] + '...' if len(kb.content) > 200 else kb.content,
                        'similarity': 0.5  # 简化的相似度计算
                    })
        
        # 返回结果
        return JsonResponse({
            'results': results,
            'count': len(results)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': '无效的JSON格式'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'error': f'处理请求时出错: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_service_status(request):
    """
    服务状态接口
    
    与原有/status接口兼容
    """
    try:
        # 获取模型服务状态
        status = get_model_status()
        
        # 返回结果
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({
            'error': f'获取服务状态时出错: {str(e)}'
        }, status=500) 