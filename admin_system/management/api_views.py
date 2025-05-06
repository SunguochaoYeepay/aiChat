"""
提示词模板 API 视图
"""
import json
import os
import subprocess
import psutil
from pathlib import Path
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, permissions, parsers
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import PromptTemplate, KnowledgeBase, ServiceControl, ModelConfig, KnowledgeChunk
from .serializers import (
    PromptTemplateSerializer, PromptTemplateCategorySerializer, 
    KnowledgeBaseSerializer, KnowledgeChunkSerializer,
    ServiceControlSerializer, ModelConfigSerializer
)
from .prompt_manager import prompt_manager


class PromptTemplateViewSet(viewsets.ModelViewSet):
    """提示词模板 API 视图集"""
    queryset = PromptTemplate.objects.all().order_by('name')
    serializer_class = PromptTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有提示词模板分类"""
        templates = {}
        for prompt in PromptTemplate.objects.all():
            category, _, type_name = prompt.name.partition('.')
            if category not in templates:
                templates[category] = {}
            templates[category][type_name] = prompt.content
        
        serialized_data = []
        for category, types in templates.items():
            serialized_data.append({
                'category': category,
                'types': types
            })
        
        serializer = PromptTemplateCategorySerializer(serialized_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def refresh_cache(self, request):
        """刷新提示词模板缓存"""
        prompt_manager.refresh_cache()
        return Response({'status': 'success', 'message': '提示词模板缓存已刷新'})
    
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """重置提示词模板为默认值"""
        try:
            with transaction.atomic():
                # 删除所有现有模板
                PromptTemplate.objects.all().delete()
                
                # 创建默认模板
                default_templates = {
                    'chat': {
                        'general': '你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}',
                        'creative': '你是一个创意写作助手，请用生动的语言回答问题。\n\n用户问题: {query}\n\n历史对话: {history}',
                        'expert': '你是该领域的专家，请提供专业、详细的回答。\n\n用户问题: {query}\n\n历史对话: {history}',
                        'concise': '你是一个简洁明了的助手，请用精炼的语言回答问题。\n\n用户问题: {query}\n\n历史对话: {history}'
                    },
                    'image_analysis': {
                        'general': '分析这张图片并描述你看到的内容。\n\n用户问题: {query}',
                        'detail': '详细分析这张图片的各个元素，包括颜色、构图和可能的含义。\n\n用户问题: {query}',
                        'object': '识别图片中的主要物体，并提供边界框标注。\n\n用户问题: {query}',
                        'design': '从设计角度分析这张图片的布局、颜色搭配、排版等元素。\n\n用户问题: {query}'
                    },
                    'search': {
                        'general': '请基于以下知识回答问题:\n\n{content}\n\n问题: {query}',
                        'concise': '请基于以下知识用简洁的语言回答问题:\n\n{content}\n\n问题: {query}',
                        'expert': '作为专家，请基于以下知识提供专业详细的回答:\n\n{content}\n\n问题: {query}',
                        'rag': '你是一个知识库助手。请只使用提供的参考信息回答问题，不要添加其他信息。如果参考信息不足以回答问题，请明确说明。\n\n参考信息:\n{content}\n\n问题: {query}'
                    },
                    'topic_matching': {
                        'general': '判断用户查询与哪个主题最相关:\n\n主题列表: {topics}\n\n用户查询: {query}',
                        'design': '判断用户的设计相关查询属于哪个设计领域:\n\n设计领域: {topics}\n\n用户查询: {query}'
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
                
                # 刷新缓存
                prompt_manager.refresh_cache()
                
                return Response({
                    'status': 'success',
                    'message': '提示词模板已重置为默认值'
                })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新提示词模板"""
        try:
            data = request.data
            
            with transaction.atomic():
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
                
                # 刷新缓存
                prompt_manager.refresh_cache()
                
                return Response({
                    'status': 'success',
                    'message': '提示词模板保存成功'
                })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """知识库 API 视图集"""
    queryset = KnowledgeBase.objects.all().order_by('-updated_at')
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
    @action(detail=False, methods=['post'])
    def import_directory(self, request):
        """从目录导入知识库文件"""
        try:
            directory = request.data.get('directory')
            if not directory:
                return Response({
                    'status': 'error',
                    'message': '请提供导入目录路径'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 确保目录存在
            dir_path = Path(directory)
            if not dir_path.exists() or not dir_path.is_dir():
                return Response({
                    'status': 'error',
                    'message': f'目录 {directory} 不存在或不是有效目录'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 导入文件
            imported_count = 0
            for md_file in dir_path.glob('*.md'):
                # 检查文件是否已经导入
                file_path = str(md_file)
                if KnowledgeBase.objects.filter(file_path=file_path).exists():
                    continue
                
                # 读取文件内容
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 创建知识库记录
                name = os.path.splitext(md_file.name)[0]  # 文件名作为知识库名称
                KnowledgeBase.objects.create(
                    name=name,
                    description=f"{name}知识库文档",
                    file_path=file_path,
                    content=content
                )
                imported_count += 1
            
            return Response({
                'status': 'success',
                'message': f'成功导入{imported_count}个知识库文档'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """上传知识库文件"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({
                    'status': 'error',
                    'message': '未提供文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查文件类型
            filename = file.name
            if not filename.lower().endswith('.md'):
                return Response({
                    'status': 'error',
                    'message': '只支持导入Markdown文件(.md)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 读取文件内容
            content = file.read().decode('utf-8')
            
            # 创建知识库记录
            name = os.path.splitext(filename)[0]  # 文件名作为知识库名称
            kb = KnowledgeBase.objects.create(
                name=name,
                description=f"{name}知识库文档",
                content=content
            )
            
            return Response({
                'status': 'success',
                'message': f'知识库文档 {name} 上传成功',
                'id': kb.id
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['post'])
    def index(self, request, pk=None):
        """向量化知识库"""
        try:
            knowledge_base = self.get_object()
            
            # 导入向量化模块
            from vector_search.indexing import index_knowledge_base
            
            # 执行向量化
            result = index_knowledge_base(knowledge_base.id)
            
            if result.get('status') == 'success':
                return Response({
                    'status': 'success',
                    'message': result.get('message', '知识库向量化成功')
                })
            else:
                return Response({
                    'status': 'error',
                    'message': result.get('message', '知识库向量化失败')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ImportError:
            return Response({
                'status': 'error',
                'message': '向量化模块未找到'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KnowledgeChunkViewSet(viewsets.ModelViewSet):
    """知识库分块 API 视图集"""
    queryset = KnowledgeChunk.objects.all().order_by('knowledge_base', 'id')
    serializer_class = KnowledgeChunkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """支持按知识库过滤"""
        queryset = super().get_queryset()
        kb_id = self.request.query_params.get('knowledge_base', None)
        if kb_id is not None:
            queryset = queryset.filter(knowledge_base_id=kb_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def vectorize(self, request, pk=None):
        """向量化单个分块"""
        try:
            chunk = self.get_object()
            
            # 导入向量化模块
            from vector_search.indexing import index_chunk
            
            # 执行向量化
            result = index_chunk(chunk.id)
            
            if result.get('status') == 'success':
                return Response({
                    'status': 'success',
                    'message': f'分块 #{pk} 向量化成功'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': result.get('message', '向量化过程中发生错误')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceControlViewSet(viewsets.ModelViewSet):
    """服务控制 API 视图集"""
    queryset = ServiceControl.objects.all().order_by('name')
    serializer_class = ServiceControlSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动服务"""
        try:
            service = self.get_object()
            
            if service.status == 'running':
                return Response({
                    'status': 'warning',
                    'message': f'服务 {service.name} 已在运行中'
                })
                
            # 执行启动命令
            process = subprocess.Popen(
                service.command, 
                shell=True, 
                stdin=None,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # 更新服务状态
            service.status = 'running'
            service.pid = process.pid
            service.save()
            
            return Response({
                'status': 'success',
                'message': f'服务 {service.name} 启动成功',
                'pid': process.pid
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'启动服务失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """停止服务"""
        try:
            service = self.get_object()
            
            if service.status != 'running':
                return Response({
                    'status': 'warning',
                    'message': f'服务 {service.name} 当前未运行'
                })
                
            # 根据PID停止进程
            if service.pid:
                try:
                    # 尝试终止进程
                    process = psutil.Process(service.pid)
                    process.terminate()
                    # 等待进程终止
                    gone, alive = psutil.wait_procs([process], timeout=3)
                    if alive:
                        # 如果进程仍在运行，强制终止
                        process.kill()
                except psutil.NoSuchProcess:
                    # 进程已不存在
                    pass
            
            # 更新服务状态
            service.status = 'stopped'
            service.pid = None
            service.save()
            
            return Response({
                'status': 'success',
                'message': f'服务 {service.name} 已停止'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'停止服务失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def refresh_status(self, request):
        """刷新所有服务状态"""
        try:
            for service in ServiceControl.objects.all():
                if service.pid:
                    try:
                        # 检查进程是否存在
                        process = psutil.Process(service.pid)
                        if process.is_running():
                            # 进程存在但状态不正确，更新状态
                            if service.status != 'running':
                                service.status = 'running'
                                service.save()
                            continue
                    except psutil.NoSuchProcess:
                        pass
                    
                    # 进程不存在或已终止，更新状态
                    if service.status == 'running':
                        service.status = 'stopped'
                        service.pid = None
                        service.save()
            
            serializer = self.get_serializer(ServiceControl.objects.all(), many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'刷新服务状态失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelConfigViewSet(viewsets.ModelViewSet):
    """模型配置 API 视图集"""
    queryset = ModelConfig.objects.all().order_by('-is_active', 'name')
    serializer_class = ModelConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活模型配置"""
        try:
            config = self.get_object()
            
            # 如果已经激活，不做操作
            if config.is_active:
                return Response({
                    'status': 'warning',
                    'message': f'模型配置 {config.name} 已处于激活状态'
                })
                
            # 更新激活状态（模型的save方法会处理将其他配置设为非激活）
            config.is_active = True
            config.save()
            
            return Response({
                'status': 'success',
                'message': f'模型配置 {config.name} 已激活'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'激活模型配置失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reload_model(self, request, pk=None):
        """重新加载模型"""
        try:
            config = self.get_object()
            
            # 确保是激活的配置
            if not config.is_active:
                return Response({
                    'status': 'error',
                    'message': '只能重新加载激活状态的模型配置'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 导入模型加载模块
            from core.model_service import reload_model
            
            # 重新加载模型
            result = reload_model(config.id)
            
            if result.get('status') == 'success':
                return Response({
                    'status': 'success',
                    'message': f'模型 {config.name} 重新加载成功'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': result.get('message', '重新加载模型过程中发生错误')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ImportError:
            return Response({
                'status': 'error',
                'message': '无法导入模型加载模块，请确认core模块配置正确'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'重新加载模型失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardViewSet(viewsets.ViewSet):
    """仪表盘 API 视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取仪表盘统计数据"""
        try:
            # 统计提示词模板数据
            template_count = PromptTemplate.objects.count()
            template_categories = len(set(t.name.split('.')[0] for t in PromptTemplate.objects.all()))
            
            # 统计知识库数据
            knowledge_base_count = KnowledgeBase.objects.count()
            document_count = KnowledgeChunk.objects.count()
            
            # 获取服务状态
            model_service_status = ServiceControl.objects.filter(name__icontains='model').first()
            api_service_status = ServiceControl.objects.filter(name__icontains='api').first()
            
            model_status = model_service_status.status if model_service_status else 'unknown'
            api_status = api_service_status.status if api_service_status else 'unknown'
            
            # 获取API调用统计(模拟数据)
            # 在实际实现中，应从API调用记录表中统计
            # 这里需要添加一个APICall模型来记录API调用
            today = timezone.now().date()
            
            # 模拟数据，实际应从数据库中获取
            api_calls_today = 128
            api_calls_total = 5763
            
            return Response({
                'template_count': template_count,
                'category_count': template_categories,
                'knowledge_base_count': knowledge_base_count,
                'document_count': document_count,
                'system_status': {
                    'model_status': model_status,
                    'api_status': api_status
                },
                'api_calls': {
                    'today': api_calls_today,
                    'total': api_calls_total
                },
                'recent_activities': [
                    {
                        'title': '更新了聊天提示词模板',
                        'time': '2023-12-15 14:30',
                        'type': 'template'
                    },
                    {
                        'title': '添加了新的知识库文档',
                        'time': '2023-12-15 11:20',
                        'type': 'knowledge'
                    },
                    {
                        'title': '重置了默认提示词',
                        'time': '2023-12-14 16:45',
                        'type': 'template'
                    },
                    {
                        'title': '优化了搜索相关提示词',
                        'time': '2023-12-14 10:15',
                        'type': 'template'
                    },
                    {
                        'title': '更新了系统配置',
                        'time': '2023-12-13 09:30',
                        'type': 'system'
                    }
                ],
                'prompt_usage': {
                    'chat': 45,
                    'search': 30,
                    'image_analysis': 15,
                    'topic_matching': 10
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 