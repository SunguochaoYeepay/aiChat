from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import VectorIndex
from .utils import vector_search, import_knowledge_base_to_vector, import_prompt_templates_to_vector, import_all_to_vector

def vector_search_ui(request):
    """向量搜索界面"""
    # 获取所有索引
    indices = VectorIndex.objects.all()
    return render(request, 'vector_search/search.html', {'indices': indices})

@csrf_exempt
def api_search(request):
    """向量搜索API"""
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body)
        index_name = data.get('index', '')
        query = data.get('query', '')
        top_k = int(data.get('top_k', 5))
        
        if not index_name or not query:
            return JsonResponse({'error': '缺少必要参数'}, status=400)
        
        try:
            index = VectorIndex.objects.get(name=index_name)
        except VectorIndex.DoesNotExist:
            return JsonResponse({'error': f'索引不存在: {index_name}'}, status=404)
        
        results = vector_search(index, query, top_k)
        return JsonResponse({'results': results})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_import_kb(request):
    """导入知识库到向量索引"""
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body) if request.body else {}
        index_name = data.get('index', 'knowledge_base')
        
        result = import_knowledge_base_to_vector(index_name)
        return JsonResponse({'success': True, 'result': result})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_import_prompt_templates(request):
    """导入提示词模板到向量索引"""
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body) if request.body else {}
        index_name = data.get('index', 'prompt_templates')
        
        result = import_prompt_templates_to_vector(index_name)
        return JsonResponse({'success': True, 'result': result})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_import_all(request):
    """导入所有资源（知识库和提示词模板）到向量索引"""
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        data = json.loads(request.body) if request.body else {}
        index_name = data.get('index', 'combined_index')
        
        result = import_all_to_vector(index_name)
        return JsonResponse({'success': True, 'result': result})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
