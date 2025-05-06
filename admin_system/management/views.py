from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import os
import json
import subprocess
from pathlib import Path
from .models import KnowledgeBase, ServiceControl, PromptTemplate, ModelConfig
from django.views.generic import TemplateView
from django.conf import settings

def import_knowledge_base(request):
    """导入知识库文件"""
    if request.method == 'POST':
        try:
            # 获取知识库目录路径
            kb_dir = Path('knowledge_base')
            if not kb_dir.exists():
                return JsonResponse({'status': 'error', 'message': '知识库目录不存在'})
            
            imported_count = 0
            # 遍历目录中的所有Markdown文件
            for md_file in kb_dir.glob('*.md'):
                # 检查文件是否已经导入
                filename = md_file.name
                file_path = str(md_file)
                
                # 如果文件已存在，则跳过
                if KnowledgeBase.objects.filter(file_path=file_path).exists():
                    continue
                
                # 读取文件内容
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 创建知识库记录
                name = os.path.splitext(filename)[0]  # 文件名作为知识库名称
                kb = KnowledgeBase(
                    name=name,
                    description=f"{name}知识库文档",
                    file_path=file_path,
                    content=content
                )
                kb.save()
                imported_count += 1
            
            return JsonResponse({
                'status': 'success', 
                'message': f'成功导入{imported_count}个知识库文档'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'management/import_kb.html')

@csrf_exempt
def manage_service(request, action):
    """管理服务的启动和停止"""
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        try:
            service = ServiceControl.objects.get(id=service_id)
            
            if action == 'start':
                # 启动服务
                process = subprocess.Popen(service.command, shell=True)
                service.pid = process.pid
                service.status = 'running'
                service.save()
                return JsonResponse({'status': 'success', 'message': f'服务 {service.name} 已启动'})
            
            elif action == 'stop':
                # 停止服务
                if service.pid:
                    if os.name == 'nt':  # Windows
                        os.system(f"taskkill /F /PID {service.pid}")
                    else:  # Linux/Unix
                        os.system(f"kill -9 {service.pid}")
                    
                    service.status = 'stopped'
                    service.pid = None
                    service.save()
                    return JsonResponse({'status': 'success', 'message': f'服务 {service.name} 已停止'})
                else:
                    return JsonResponse({'status': 'error', 'message': '无法找到服务进程ID'})
            
            else:
                return JsonResponse({'status': 'error', 'message': '未知操作'})
                
        except ServiceControl.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '服务不存在'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

class VueAppView(TemplateView):
    """Vue 前端应用视图"""
    template_name = 'vue_index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加初始状态数据
        context['initial_state'] = json.dumps({
            'api_base_url': '/api/v1',
            'csrf_token': self.request.META.get('CSRF_COOKIE', '')
        })
        return context

def prompt_editor(request):
    """提示词编辑器视图"""
    return render(request, 'management/prompt_editor.html')

def prompt_manager(request):
    """
    提示词模板管理器视图
    
    允许用户管理不同类型的提示词模板
    """
    template_categories = {}
    
    # 获取所有提示词模板并按类别分组
    for prompt in PromptTemplate.objects.all():
        category, _, type_name = prompt.name.partition('.')
        if category not in template_categories:
            template_categories[category] = {}
        template_categories[category][type_name] = prompt.content
    
    context = {
        'template_categories': template_categories
    }
    
    return render(request, 'management/prompt_manager.html', context)

@csrf_exempt
def prompt_templates(request):
    """获取或保存提示词模板"""
    if request.method == 'GET':
        # 从数据库获取所有提示词模板
        templates = {}
        for prompt in PromptTemplate.objects.all():
            category, _, type_name = prompt.name.partition('.')
            if category not in templates:
                templates[category] = {}
            templates[category][type_name] = prompt.content
        
        return JsonResponse(templates)
    
    elif request.method == 'POST':
        try:
            # 保存提交的模板
            data = json.loads(request.body)
            for category, types in data.items():
                for type_name, content in types.items():
                    prompt_name = f"{category}.{type_name}"
                    prompt, created = PromptTemplate.objects.update_or_create(
                        name=prompt_name,
                        defaults={
                            'content': content,
                            'description': f"{category}类别的{type_name}提示词模板"
                        }
                    )
            
            return JsonResponse({'status': 'success', 'message': '提示词模板保存成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@csrf_exempt
def get_templates_list(request):
    """获取所有提示词模板列表"""
    try:
        templates = []
        for prompt in PromptTemplate.objects.all().order_by('name'):
            templates.append({
                'id': prompt.id,
                'name': prompt.name,
                'description': prompt.description,
                'created_at': prompt.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': prompt.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({'templates': templates})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def get_template(request, template_id):
    """获取单个提示词模板"""
    try:
        prompt = get_object_or_404(PromptTemplate, id=template_id)
        return JsonResponse({
            'id': prompt.id,
            'name': prompt.name,
            'description': prompt.description,
            'content': prompt.content,
            'created_at': prompt.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': prompt.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def create_template(request):
    """创建新的提示词模板"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            content = data.get('content')
            
            if not name or not content:
                return JsonResponse({'status': 'error', 'message': '名称和内容不能为空'})
            
            if PromptTemplate.objects.filter(name=name).exists():
                return JsonResponse({'status': 'error', 'message': f'名称"{name}"已存在'})
            
            prompt = PromptTemplate.objects.create(
                name=name,
                description=description,
                content=content
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': '提示词模板创建成功',
                'id': prompt.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

@csrf_exempt
def update_template(request, template_id):
    """更新提示词模板"""
    if request.method == 'POST':
        try:
            prompt = get_object_or_404(PromptTemplate, id=template_id)
            
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            content = data.get('content')
            
            if not name or not content:
                return JsonResponse({'status': 'error', 'message': '名称和内容不能为空'})
            
            # 检查名称是否已存在（排除当前模板）
            if PromptTemplate.objects.filter(name=name).exclude(id=template_id).exists():
                return JsonResponse({'status': 'error', 'message': f'名称"{name}"已存在'})
            
            prompt.name = name
            prompt.description = description
            prompt.content = content
            prompt.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': '提示词模板更新成功'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

@csrf_exempt
def delete_template(request, template_id):
    """删除提示词模板"""
    if request.method == 'POST':
        try:
            prompt = get_object_or_404(PromptTemplate, id=template_id)
            name = prompt.name
            prompt.delete()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'提示词模板"{name}"已删除'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

@csrf_exempt
def refresh_templates(request):
    """重置提示词模板为默认值"""
    if request.method == 'POST':
        try:
            # 删除所有现有模板
            PromptTemplate.objects.all().delete()
            
            # 创建默认模板
            default_templates = {
                'chat': {
                    'general': '你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}',
                    'creative': '你是一个创意写作助手，请用生动的语言回答问题。\n\n用户问题: {query}\n\n历史对话: {history}',
                    'expert': '你是该领域的专家，请提供专业、详细的回答。\n\n用户问题: {query}\n\n历史对话: {history}'
                },
                'image_analysis': {
                    'general': '分析这张图片并描述你看到的内容。\n\n用户问题: {query}',
                    'detail': '详细分析这张图片的各个元素，包括颜色、构图和可能的含义。\n\n用户问题: {query}',
                    'object': '识别图片中的主要物体，并提供边界框标注。\n\n用户问题: {query}'
                },
                'search': {
                    'general': '请基于以下知识回答问题:\n\n{content}\n\n问题: {query}',
                    'concise': '请基于以下知识用简洁的语言回答问题:\n\n{content}\n\n问题: {query}',
                    'expert': '作为专家，请基于以下知识提供专业详细的回答:\n\n{content}\n\n问题: {query}'
                }
            }
            
            # 保存默认模板到数据库
            for category, types in default_templates.items():
                for type_name, content in types.items():
                    PromptTemplate.objects.create(
                        name=f"{category}.{type_name}",
                        content=content,
                        description=f"{category}类别的{type_name}提示词模板"
                    )
            
            return JsonResponse({
                'status': 'success',
                'message': '提示词模板已重置为默认值',
                'templates': default_templates
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

def model_service_status(request):
    """获取模型服务状态"""
    try:
        # 导入模型服务模块
        from core.model_service import get_service_status
        
        # 获取服务状态
        status = get_service_status()
        
        # 获取所有模型配置
        configs = []
        for config in ModelConfig.objects.all().order_by('-is_active', 'name'):
            configs.append({
                'id': config.id,
                'name': config.name,
                'model_path': config.model_path,
                'device': config.device,
                'is_active': config.is_active,
                'precision': config.precision,
                'batch_size': config.batch_size,
                'description': config.description,
                'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 创建上下文
        context = {
            'service_status': status,
            'model_configs': configs,
            'active_config': next((c for c in configs if c['is_active']), None)
        }
        
        # 根据请求类型返回
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(context)
        else:
            return render(request, 'management/model_status.html', context)
            
    except ImportError:
        context = {
            'service_status': {
                'status': 'error',
                'message': '模型服务模块未找到',
                'model_loaded': False
            },
            'model_configs': [],
            'active_config': None
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(context)
        else:
            return render(request, 'management/model_status.html', context)
            
    except Exception as e:
        context = {
            'service_status': {
                'status': 'error',
                'message': f'获取状态时出错: {str(e)}',
                'model_loaded': False
            },
            'model_configs': [],
            'active_config': None
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(context)
        else:
            return render(request, 'management/model_status.html', context)

@csrf_exempt
def reload_model(request):
    """重新加载模型"""
    if request.method == 'POST':
        try:
            # 导入模型服务模块
            from core.model_service import reload_model as reload_model_service
            
            # 获取模型ID
            model_id = request.POST.get('model_id')
            
            # 重新加载模型
            result = reload_model_service(model_id)
            
            return JsonResponse(result)
            
        except ImportError:
            return JsonResponse({
                'status': 'error',
                'message': '模型服务模块未找到'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'重新加载模型时出错: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': '仅支持POST请求'
    })

def vector_search_ui(request):
    """知识库向量搜索界面"""
    return render(request, 'management/vector_search.html')

def management_index(request):
    """管理首页视图"""
    # 获取基本统计信息
    stats = {
        'total_prompts': PromptTemplate.objects.count(),
        'total_kb': KnowledgeBase.objects.count(),
        'total_services': ServiceControl.objects.count(),
        'model_configs': ModelConfig.objects.count()
    }
    
    # 检查模型服务状态
    try:
        from core.model_service import get_service_status
        model_status = get_service_status()
    except Exception:
        model_status = {'status': 'unknown', 'model_loaded': False}
    
    # 获取最近的知识库
    recent_kb = KnowledgeBase.objects.order_by('-updated_at')[:5]
    
    # 获取最近的提示词模板
    recent_prompts = PromptTemplate.objects.order_by('-updated_at')[:5]
    
    context = {
        'stats': stats,
        'model_status': model_status,
        'recent_kb': recent_kb,
        'recent_prompts': recent_prompts,
    }
    
    return render(request, 'management/index.html', context)

def knowledge_base(request):
    """知识库管理视图"""
    # 获取所有知识库
    kb_list = KnowledgeBase.objects.all().order_by('-updated_at')
    
    # 按查询过滤（如果有）
    query = request.GET.get('q', '')
    if query:
        kb_list = kb_list.filter(name__icontains=query) | kb_list.filter(content__icontains=query)
    
    context = {
        'kb_list': kb_list,
        'total_count': KnowledgeBase.objects.count(),
        'query': query
    }
    
    return render(request, 'management/knowledge_base.html', context)

def service_control(request):
    """服务控制视图"""
    # 获取所有服务
    services = ServiceControl.objects.all().order_by('name')
    
    # 处理服务启动/停止请求
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        action = request.POST.get('action')
        
        if service_id and action in ['start', 'stop']:
            service = get_object_or_404(ServiceControl, id=service_id)
            
            if action == 'start':
                # 启动服务
                try:
                    process = subprocess.Popen(service.command, shell=True)
                    service.pid = process.pid
                    service.status = 'running'
                    service.save()
                    messages.success(request, f'服务 {service.name} 已启动')
                except Exception as e:
                    messages.error(request, f'启动服务失败: {str(e)}')
                    
            elif action == 'stop':
                # 停止服务
                try:
                    if service.pid:
                        if os.name == 'nt':  # Windows
                            os.system(f"taskkill /F /PID {service.pid}")
                        else:  # Linux/Unix
                            os.system(f"kill -9 {service.pid}")
                        
                    service.status = 'stopped'
                    service.pid = None
                    service.save()
                    messages.success(request, f'服务 {service.name} 已停止')
                except Exception as e:
                    messages.error(request, f'停止服务失败: {str(e)}')
    
    context = {
        'services': services
    }
    
    return render(request, 'management/service_control.html', context)

def models_config(request):
    """模型配置视图"""
    # 获取所有模型配置
    configs = ModelConfig.objects.all().order_by('-is_active', 'name')
    
    context = {
        'configs': configs,
        'active_config': ModelConfig.objects.filter(is_active=True).first()
    }
    
    return render(request, 'management/models_config.html', context)

def save_model_config(request):
    """保存模型配置"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            config_id = request.POST.get('config_id')
            name = request.POST.get('name')
            model_path = request.POST.get('model_path')
            device = request.POST.get('device', 'cuda')
            precision = request.POST.get('precision', 'float16')
            batch_size = request.POST.get('batch_size', 1)
            description = request.POST.get('description', '')
            is_active = 'is_active' in request.POST
            
            if config_id:
                # 更新现有配置
                config = get_object_or_404(ModelConfig, id=config_id)
                config.name = name
                config.model_path = model_path
                config.device = device
                config.precision = precision
                config.batch_size = batch_size
                config.description = description
                
                # 如果选为活跃配置，重置其他配置
                if is_active and not config.is_active:
                    ModelConfig.objects.filter(is_active=True).update(is_active=False)
                    config.is_active = True
                    
                config.save()
                messages.success(request, '模型配置已更新')
            else:
                # 创建新配置
                # 如果选为活跃配置，重置其他配置
                if is_active:
                    ModelConfig.objects.filter(is_active=True).update(is_active=False)
                
                # 创建新配置
                ModelConfig.objects.create(
                    name=name,
                    model_path=model_path,
                    device=device,
                    precision=precision,
                    batch_size=batch_size,
                    description=description,
                    is_active=is_active
                )
                messages.success(request, '模型配置已创建')
                
            return redirect('management:models_config')
            
        except Exception as e:
            messages.error(request, f'保存模型配置失败: {str(e)}')
            return redirect('management:models_config')
    
    # 对于GET请求，重定向到配置页面
    return redirect('management:models_config')

@csrf_exempt
def save_prompt_template(request):
    """保存提示词模板"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            template_id = data.get('id')
            name = data.get('name')
            content = data.get('content')
            description = data.get('description', '')
            
            if not name or not content:
                return JsonResponse({'status': 'error', 'message': '名称和内容不能为空'})
            
            if template_id:
                # 更新现有模板
                template = get_object_or_404(PromptTemplate, id=template_id)
                template.name = name
                template.content = content
                template.description = description
                template.save()
                return JsonResponse({'status': 'success', 'message': '模板已更新'})
            else:
                # 创建新模板
                # 检查名称是否已存在
                if PromptTemplate.objects.filter(name=name).exists():
                    return JsonResponse({'status': 'error', 'message': f'名称"{name}"已存在'})
                
                template = PromptTemplate.objects.create(
                    name=name,
                    content=content,
                    description=description
                )
                return JsonResponse({'status': 'success', 'message': '模板已创建'})
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON格式'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@csrf_exempt
def delete_prompt_template(request):
    """删除提示词模板"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            template_id = data.get('id')
            
            if not template_id:
                return JsonResponse({'status': 'error', 'message': '缺少模板ID'})
            
            template = get_object_or_404(PromptTemplate, id=template_id)
            template.delete()
            
            return JsonResponse({'status': 'success', 'message': '模板已删除'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON格式'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@csrf_exempt
def reset_prompt_templates(request):
    """重置提示词模板"""
    return refresh_templates(request)
