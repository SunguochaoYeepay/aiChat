"""
API视图函数 - 提供与原系统兼容的API接口

此模块实现了与原有FastAPI系统兼容的HTTP API接口，确保现有前端能继续正常工作。
"""
import json
import time
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 导入核心功能模块
from core.image_analysis import analyze_image as analyze_image_core
from core.text_processing import chat_completion
from core.model_service import get_service_status as get_model_status
from management.models import KnowledgeBase
from knowledge_base.services import search_knowledge_base as kb_vector_search

# 导入API模型
from .models import APIEndpoint, APIKey

# 导入管理员装饰器
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect

def index_view(request):
    """
    首页视图函数
    
    处理根路径"/"的请求
    """
    return HttpResponse(
        '<h1>设计助手API服务</h1>'
        '<p>API服务已正常运行。</p>'
        '<p>可用API接口:</p>'
        '<ul>'
        '<li>/api/analyze - 图像分析接口</li>'
        '<li>/api/v1/chat/completions - 聊天完成接口</li>'
        '<li>/api/search - 知识库搜索接口</li>'
        '<li>/api/status - 服务状态接口</li>'
        '</ul>'
    )

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

# 添加新的API文档视图
@staff_member_required
def api_docs_view(request):
    """
    API文档视图
    
    为管理员提供API接口文档
    """
    # 获取所有API端点
    endpoints = APIEndpoint.objects.all().order_by('path')
    
    # 按分类分组API端点
    api_groups = {}
    for endpoint in endpoints:
        # 根据路径前缀分组
        path_parts = endpoint.path.split('/')
        if len(path_parts) > 1:
            prefix = path_parts[1] if path_parts[0] == '' else path_parts[0]
            if prefix not in api_groups:
                api_groups[prefix] = []
            api_groups[prefix].append(endpoint)
        else:
            # 没有前缀的放入根分组
            if 'root' not in api_groups:
                api_groups['root'] = []
            api_groups['root'].append(endpoint)
    
    # 计算统计信息
    total_apis = endpoints.count()
    active_apis = endpoints.filter(status='active').count()
    deprecated_apis = endpoints.filter(status='deprecated').count()
    
    # 渲染模板
    return render(request, 'api/api_docs.html', {
        'api_groups': api_groups,
        'total_apis': total_apis,
        'active_apis': active_apis,
        'deprecated_apis': deprecated_apis,
    })

@staff_member_required
@csrf_exempt
def api_import_view(request):
    """
    API批量导入视图
    
    允许管理员从Swagger/OpenAPI规范批量导入API端点
    """
    if request.method == 'POST':
        try:
            # 处理上传的OpenAPI规范
            if 'openapi_file' in request.FILES:
                # 从文件中读取规范
                openapi_file = request.FILES['openapi_file']
                openapi_content = openapi_file.read().decode('utf-8')
                openapi_data = json.loads(openapi_content)
            elif 'openapi_content' in request.POST:
                # 从文本区域中读取规范
                openapi_content = request.POST['openapi_content']
                openapi_data = json.loads(openapi_content)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '未提供OpenAPI规范'
                }, status=400)
            
            # 处理OpenAPI规范
            import_results = process_openapi_spec(openapi_data)
            
            # 返回结果
            return JsonResponse({
                'status': 'success',
                'imported': import_results['imported'],
                'skipped': import_results['skipped'],
                'message': f'成功导入 {import_results["imported"]} 个API, 跳过 {import_results["skipped"]} 个已存在的API'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '无效的JSON格式'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'导入API时出错: {str(e)}'
            }, status=500)
    
    # GET请求显示导入表单
    return render(request, 'api/api_import.html')

def process_openapi_spec(openapi_data):
    """处理OpenAPI规范，导入API端点"""
    results = {'imported': 0, 'skipped': 0}
    
    # 处理OpenAPI 3.0规范
    if 'openapi' in openapi_data and openapi_data['openapi'].startswith('3.'):
        # 获取API信息
        info = openapi_data.get('info', {})
        # 获取API路径
        paths = openapi_data.get('paths', {})
        
        # 处理每个API路径
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete']:
                    # 检查API是否已存在
                    if not APIEndpoint.objects.filter(path=path, method=method.upper()).exists():
                        # 创建新的API端点
                        endpoint = APIEndpoint(
                            name=details.get('summary', f"{method.upper()} {path}"),
                            description=details.get('description', ''),
                            path=path,
                            method=method.upper(),
                            status='active',
                            # 处理请求体
                            request_schema=details.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {}),
                            # 处理响应
                            response_schema=details.get('responses', {}).get('200', {}).get('content', {}).get('application/json', {}).get('schema', {})
                        )
                        endpoint.save()
                        results['imported'] += 1
                    else:
                        results['skipped'] += 1
    
    return results 