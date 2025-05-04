# AI图像分析服务与Django Admin系统整合方案

## 背景

目前系统由两部分组成：
1. 基于FastAPI的AI图像分析服务（`gpu_model_server.py`）
2. 基于Django的管理系统（`admin_system`）

整合目标是将AI图像分析服务完全集成到Django管理系统中，形成一个统一的应用，同时保持现有API接口的兼容性。

## 需求概述

1. **保留现有功能**：保持原有图片识别和问答功能不变
2. **模型配置管理**：在Django admin中添加模型配置管理能力
3. **保留WebSocket功能**：确保WebSocket接口持续可用
4. **使用统一数据库**：用SQLite数据库代替文件系统知识库
5. **单一服务部署**：整合后作为单一服务部署
6. **舍弃测试页面**：现有的前端测试页面可以舍弃
7. **API兼容性**：保持与现有系统相同的API接口，确保现有前端正常工作

## 技术方案

### 1. 模型配置管理

在Django admin中添加模型配置管理功能：

```python
# 在admin_system/management/models.py中添加
class ModelConfig(models.Model):
    """模型配置"""
    name = models.CharField('配置名称', max_length=100)
    model_path = models.CharField('模型路径', max_length=255)
    device = models.CharField('设备', max_length=20, choices=[('cuda', 'GPU'), ('cpu', 'CPU')], default='cuda')
    is_active = models.BooleanField('是否激活', default=False)
    batch_size = models.IntegerField('批处理大小', default=1)
    precision = models.CharField('精度', max_length=20, 
                               choices=[('float16', '半精度'), ('float32', '全精度')],
                               default='float16')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '模型配置'
        verbose_name_plural = '模型配置'
    
    def __str__(self):
        return f"{self.name} ({self.get_device_display()})"
```

### 2. 模型服务模块化重构

创建`admin_system/core`包，将图像分析功能重构为可导入的模块：

```
admin_system/core/
  __init__.py
  model_service.py  # 模型加载和服务
  image_analysis.py  # 图像分析功能
  text_processing.py  # 文本处理功能
  utils.py  # 通用工具函数
  websocket/  # WebSocket相关功能
    __init__.py
    managers.py  # 连接管理
    handlers.py  # 消息处理
```

### 3. API接口兼容实现

在`admin_system/api`中实现与原有系统兼容的API：

```
admin_system/api/
  __init__.py
  urls.py  # 路由配置
  views.py  # 视图函数
  websocket.py  # WebSocket处理
```

实现原有API接口：
- POST /analyze
- POST /v1/chat/completions
- POST /search
- GET /status
- WebSocket /ws/chat
- WebSocket /ws/analyze

### 4. 知识库迁移

创建知识库迁移脚本，将文件系统中的知识库迁移到数据库：

```python
# admin_system/management/management/commands/migrate_kb.py
from django.core.management.base import BaseCommand
from pathlib import Path
from management.models import KnowledgeBase
import os

class Command(BaseCommand):
    help = '将文件系统知识库迁移到数据库'
    
    def handle(self, *args, **options):
        kb_dir = Path('knowledge_base')
        if not kb_dir.exists():
            self.stdout.write(self.style.ERROR('知识库目录不存在'))
            return
        
        imported_count = 0
        for md_file in kb_dir.glob('*.md'):
            filename = md_file.name
            file_path = str(md_file)
            
            # 检查文件是否已导入
            if KnowledgeBase.objects.filter(file_path=file_path).exists():
                continue
            
            # 读取文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建知识库记录
            name = os.path.splitext(filename)[0]
            kb = KnowledgeBase(
                name=name,
                description=f"{name}知识库文档",
                file_path=file_path,
                content=content
            )
            kb.save()
            imported_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'成功导入{imported_count}个知识库文档'))
```

### 5. Django与ASGI集成支持WebSocket

配置Django项目支持ASGI和WebSocket：

```python
# admin_system/admin_system/asgi.py
import os
import sys
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

# 确保应用路径正确
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')

# 获取Django ASGI应用
django_asgi_app = get_asgi_application()

# 导入WebSocket消费者
from api.websocket import ChatConsumer, AnalyzeConsumer

# 定义WebSocket路由
websocket_urlpatterns = [
    path('ws/chat', ChatConsumer.as_asgi()),
    path('ws/analyze', AnalyzeConsumer.as_asgi()),
]

# 配置ASGI应用
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
```

### 6. 服务集成管理

实现服务管理接口，允许通过管理界面控制模型服务：

```python
# 在admin_system/management/views.py中添加
def model_service_status(request):
    """获取模型服务状态"""
    try:
        from core.model_service import get_service_status
        status = get_service_status()
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def reload_model(request):
    """重新加载模型"""
    if request.method == 'POST':
        try:
            from core.model_service import reload_model
            model_id = request.POST.get('model_id')
            result = reload_model(model_id)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})
```

### 7. 统一项目配置

创建统一的配置管理：

```python
# admin_system/core/config.py
from django.conf import settings
from management.models import ModelConfig
import os

def get_active_model_config():
    """获取当前激活的模型配置"""
    try:
        return ModelConfig.objects.get(is_active=True)
    except ModelConfig.DoesNotExist:
        # 返回默认配置
        return {
            'model_path': getattr(settings, 'DEFAULT_MODEL_PATH', 'D:/AI-DEV/models/Qwen-VL-Chat-Int4'),
            'device': getattr(settings, 'DEFAULT_DEVICE', 'cuda'),
            'batch_size': getattr(settings, 'DEFAULT_BATCH_SIZE', 1),
            'precision': getattr(settings, 'DEFAULT_PRECISION', 'float16'),
        }

def get_static_dir():
    """获取静态文件目录"""
    return os.path.join(settings.BASE_DIR, 'static')

def get_box_image_dir():
    """获取边界框图像目录"""
    box_dir = os.path.join(get_static_dir(), 'box_images')
    os.makedirs(box_dir, exist_ok=True)
    return box_dir
```

## 实施进度

### 阶段1: 基础结构设置 ✅
- [x] 创建core包结构
- [x] 添加模型配置模型
- [x] 实现配置管理功能

### 阶段2: 模型服务重构 ✅
- [x] 将gpu_model_server.py功能重构为模块
- [x] 实现模型加载和管理功能
- [x] 实现图像分析核心功能

### 阶段3: API兼容层实现 ✅
- [x] 创建API应用
- [x] 实现与原有系统兼容的API接口
- [x] 实现WebSocket支持

### 阶段4: 知识库整合 ✅
- [x] 创建知识库迁移脚本
- [x] 将文件系统知识库迁移到数据库
- [x] 整合知识库搜索功能

### 阶段5: 管理界面优化 ✅
- [x] 实现模型管理界面
- [x] 实现服务状态监控
- [x] 优化Django admin界面

### 阶段6: 测试与部署 🔄
- [x] 编写基本测试用例验证功能
- [ ] 创建统一的部署脚本
- [ ] 配置生产环境

## 下一步计划

1. 完成部署脚本，确保整个系统能够一键部署
2. 配置生产环境，确保系统在生产环境中稳定运行
3. 完善使用文档，为用户提供完整的使用指南
4. 进行系统性能优化，确保系统在高负载下仍能正常工作

## 风险与缓解措施

### 风险1: 服务中断
- **风险描述**: 重构过程可能导致现有功能暂时无法使用
- **缓解措施**: 
  - 采用增量式重构，而非一次性大改
  - 先建立新结构，逐步迁移功能，保持旧系统可用

### 风险2: 功能丢失
- **风险描述**: 重构过程中可能遗漏某些现有功能
- **缓解措施**:
  - 在重构前详细列出所有现有功能和API
  - 为每个功能创建测试用例，确保重构后仍然可用

### 风险3: 性能退化
- **风险描述**: 新系统架构可能影响模型加载和推理性能
- **缓解措施**:
  - 在重构前建立性能基准
  - 定期测试确保新系统不降低性能

### 风险4: 集成复杂性
- **风险描述**: Django和FastAPI集成可能存在技术挑战
- **缓解措施**:
  - 通过模块化方式集成，避免直接合并代码
  - 使用共享内存而非网络请求方式调用模型服务

## 资源需求

1. **开发资源**:
   - 后端开发: 1人
   - 前端开发: 暂不需要（保持现有前端）
   - 测试人员: 1人

2. **硬件资源**:
   - 开发环境: 支持CUDA的GPU服务器
   - 测试环境: 同上
   - 生产环境: 同上

3. **软件资源**:
   - Django 框架
   - Channels (用于WebSocket支持)
   - PyTorch 和 transformers 库
   - 其他依赖（详见requirements.txt）

## 交付成果

1. 完整的集成Django管理系统
2. 支持原有API接口的兼容层
3. 模型配置管理界面
4. 知识库管理功能
5. 服务状态监控功能
6. 部署和维护文档

## 成功标准

1. 所有原有API接口保持兼容
2. WebSocket功能正常工作
3. 图像分析性能不低于原有系统
4. 知识库功能正常工作
5. 服务可通过Django admin界面管理 