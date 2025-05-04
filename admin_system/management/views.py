from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import os
import json
import subprocess
from pathlib import Path
from .models import KnowledgeBase, ServiceControl, PromptTemplate

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

def prompt_editor(request):
    """提示词模板编辑器"""
    # 简单地返回静态HTML文件
    return render(request, 'management/prompt_editor.html')

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

def refresh_templates(request):
    """重置提示词模板为默认值"""
    if request.method == 'POST':
        try:
            # 删除所有现有模板
            PromptTemplate.objects.all().delete()
            
            # 创建默认模板
            default_templates = {
                'chat': {
                    'general': '你是一个AI助手，请回答用户的问题。',
                    'creative': '你是一个创意写作助手，请用生动的语言回答问题。'
                },
                'image_analysis': {
                    'general': '分析这张图片并描述你看到的内容。',
                    'detail': '详细分析这张图片的各个元素，包括颜色、构图和可能的含义。'
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
