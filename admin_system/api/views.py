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

@staff_member_required
def api_test_view(request):
    """
    API测试界面视图函数
    
    允许管理员在Web界面上测试API接口
    """
    endpoints = APIEndpoint.objects.all().order_by('path')
    api_keys = APIKey.objects.filter(is_active=True)
    
    # 获取URL中可能的endpoint_id参数
    selected_endpoint_id = request.GET.get('endpoint_id', None)
    
    context = {
        'endpoints': endpoints,
        'api_keys': api_keys,
        'selected_endpoint_id': selected_endpoint_id,
    }
    
    return render(request, 'api/api_test.html', context)

@staff_member_required
def api_endpoint_detail(request, endpoint_id):
    """
    API端点详情接口
    
    返回指定API端点的详细信息，供API测试界面使用
    """
    try:
        endpoint = APIEndpoint.objects.get(pk=endpoint_id)
        
        data = {
            'id': endpoint.id,
            'name': endpoint.name,
            'path': endpoint.path,
            'method': endpoint.method,
            'description': endpoint.description,
            'status': endpoint.status,
            'permission': endpoint.permission,
            'request_schema': endpoint.request_schema,
            'response_schema': endpoint.response_schema,
        }
        
        return JsonResponse(data)
    except APIEndpoint.DoesNotExist:
        return JsonResponse({'error': '找不到指定的API端点'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'获取API端点详情时出错: {str(e)}'}, status=500)

@staff_member_required
@csrf_exempt
def api_test_execute(request):
    """
    执行API测试接口
    
    接收API测试界面的请求，转发到实际的API端点
    """
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # 获取API端点和密钥
        endpoint_id = data.pop('endpoint_id', None) if 'endpoint_id' in data else None
        api_key = data.pop('api_key', '') if 'api_key' in data else ''
        
        if not endpoint_id:
            return JsonResponse({'error': '缺少endpoint_id参数'}, status=400)
        
        # 获取API端点信息
        try:
            endpoint = APIEndpoint.objects.get(pk=endpoint_id)
        except APIEndpoint.DoesNotExist:
            return JsonResponse({'error': '找不到指定的API端点'}, status=404)
        
        # 删除endpoint_id和空的api_key
        if 'endpoint_id' in data:
            data.pop('endpoint_id')
        
        # 准备请求参数
        request_data = {}
        
        # 处理request_body
        if 'request_body' in data and data['request_body']:
            try:
                # 尝试解析JSON
                request_data = json.loads(data.pop('request_body'))
            except:
                # 如果不是JSON，忽略它
                data.pop('request_body', None)
        
        # 处理param_开头的参数
        for key in list(data.keys()):
            if key.startswith('param_'):
                param_name = key.replace('param_', '')
                request_data[param_name] = data[key]
                data.pop(key)
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 完全忽略API密钥要求，简化测试流程
        # 不再添加X-API-Key头
        
        # 确定请求URL
        base_url = f"{request.scheme}://{request.get_host()}"
        
        # 确保路径以/开头
        path = endpoint.path
        if not path.startswith('/'):
            path = '/' + path
            
        # 处理路径，确保正确的格式
        api_url = f"{base_url}{path}"
        
        # 发送请求前打印详情，便于调试
        print(f"Testing API: {endpoint.method} {api_url}")
        print(f"Headers: {headers}")
        print(f"Request data: {request_data}")
        
        # 发送请求
        import requests
        
        try:
            if endpoint.method == 'GET':
                response = requests.get(api_url, params=request_data, headers=headers, timeout=10)
            elif endpoint.method == 'POST':
                response = requests.post(api_url, json=request_data, headers=headers, timeout=10)
            elif endpoint.method == 'PUT':
                response = requests.put(api_url, json=request_data, headers=headers, timeout=10)
            elif endpoint.method == 'DELETE':
                response = requests.delete(api_url, json=request_data, headers=headers, timeout=10)
            else:
                return JsonResponse({'error': f'不支持的请求方法: {endpoint.method}'}, status=400)
        except requests.exceptions.RequestException as req_err:
            return JsonResponse({'error': f'请求错误: {str(req_err)}'}, status=500)
        
        # 打印响应状态和头信息，便于调试
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        # 返回响应
        try:
            response_json = response.json()
            return JsonResponse(response_json, status=response.status_code, safe=False)
        except Exception as content_error:
            # 如果不是JSON响应，返回文本
            try:
                return HttpResponse(response.text, status=response.status_code, 
                                  content_type=response.headers.get('Content-Type', 'text/plain'))
            except:
                return HttpResponse(f"无法解析响应内容", status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求JSON格式'}, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"API测试错误: {str(e)}")
        print(error_trace)
        return JsonResponse({'error': f'执行API测试时出错: {str(e)}'}, status=500) 