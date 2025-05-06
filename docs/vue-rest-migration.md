# Django 到 Django REST 框架 + Vue 的迁移文档

## 迁移概述

本文档记录了将设计助手项目从传统的Django视图模式迁移到Django REST框架+Vue前端架构的过程。迁移工作在`vue-rest-refactor`分支上完成。

### 迁移目标

- 将后端API转换为RESTful风格
- 使用Vue.js创建现代化的前端界面
- 保持与原有API的兼容性
- 提高系统模块化和可维护性

### 主要变更

1. 添加了Django REST框架支持
2. 为关键模型创建了序列化器和ViewSet
3. 创建了Vue前端应用
4. 实现了前后端分离的架构

## 后端变更

### 依赖添加

添加了以下依赖:

- `djangorestframework`: 用于创建RESTful API
- `django-cors-headers`: 用于处理跨域请求

### 配置变更

在`settings.py`中添加了以下配置:

```python
INSTALLED_APPS = [
    # ...现有应用...
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    # ...现有中间件...
    'corsheaders.middleware.CorsMiddleware',  # 必须在CommonMiddleware之前
]

# REST Framework设置
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# CORS设置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Vue开发服务器
    "http://localhost:5173",  # Vite默认端口
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
]
```

### API 实现

#### 序列化器

为模型创建了序列化器，位于`management/serializers.py`:

1. **提示词模板序列化器**:
   - `PromptTemplateSerializer`: 处理单个提示词模板的序列化
   - `PromptTemplateCategorySerializer`: 处理提示词模板分类的序列化

2. **知识库序列化器**:
   - `KnowledgeBaseSerializer`: 处理知识库的序列化

#### API 视图集

创建了REST框架视图集，位于`management/api_views.py`:

1. **提示词模板视图集** (`PromptTemplateViewSet`):
   - 支持标准CRUD操作
   - 提供额外端点:
     - `/categories/`: 获取提示词模板分类
     - `/refresh_cache/`: 刷新提示词模板缓存
     - `/reset/`: 重置为默认提示词模板
     - `/batch_update/`: 批量更新提示词模板

2. **知识库视图集** (`KnowledgeBaseViewSet`):
   - 支持标准CRUD操作
   - 提供额外端点:
     - `/import_directory/`: 从目录导入知识库文件
     - `/upload/`: 上传单个知识库文件
     - `/{id}/index/`: 向量化指定知识库

#### API 路由

添加了REST框架路由，位于`management/api_urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PromptTemplateViewSet, KnowledgeBaseViewSet

router = DefaultRouter()
router.register(r'templates', PromptTemplateViewSet)
router.register(r'knowledge', KnowledgeBaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

这些路由通过主URL配置中的以下条目挂载:

```python
# REST API 路由
path('api/v1/', include('management.api_urls')),
```

### 提示词管理器

添加了提示词模板管理器，位于`management/prompt_manager.py`:

- 提供缓存管理功能
- 支持按类别获取提示词模板
- 使用单例模式确保全局一致性

### 与核心服务集成

修改了核心服务以使用新的提示词管理器:

- `chat_completion`函数更新，支持知识库搜索和提示词模板应用
- 保留了与现有API的兼容性

## 前端实现

### Vue 项目结构

创建了Vue前端项目，位于`admin_system/frontend/`:

```
frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── promptTemplates.js
│   │   └── knowledgeBase.js
│   ├── components/
│   │   └── PromptTemplateEditor.vue
│   ├── views/
│   │   ├── Dashboard.vue
│   │   ├── PromptManager.vue
│   │   ├── KnowledgeBase.vue
│   │   └── ApiTest.vue
│   ├── router/
│   │   └── index.js
│   ├── store/
│   │   └── index.js
│   ├── App.vue
│   └── main.js
├── package.json
└── vue.config.js
```

### API 服务层

为前端创建了API服务:

1. **提示词模板API** (`src/api/promptTemplates.js`):
   - 获取、创建、更新、删除提示词模板
   - 刷新缓存、重置默认值等高级功能

2. **知识库API** (`src/api/knowledgeBase.js`):
   - 获取、创建、更新、删除知识库
   - 导入目录、上传文件、向量化知识库等功能

### Vue 组件

创建了核心Vue组件:

1. **提示词模板编辑器** (`PromptTemplateEditor.vue`):
   - 编辑提示词模板内容
   - 按类别和类型组织模板
   - 批量操作功能

2. **提示词管理** (`PromptManager.vue`):
   - 提示词模板列表
   - 编辑、删除功能
   - 帮助文档

3. **知识库管理** (`KnowledgeBase.vue`):
   - 知识库列表
   - 导入、上传、查看内容功能
   - 知识库向量化

4. **API测试** (`ApiTest.vue`):
   - API接口列表
   - 可视化测试功能
   - 请求历史记录

### 状态管理

使用Vuex实现状态管理:

- 提示词模板状态
- 知识库状态
- 用户认证状态

### 路由配置

使用Vue Router配置前端路由:

```javascript
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/prompts',
    name: 'PromptManager',
    component: PromptManager
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: KnowledgeBase
  },
  {
    path: '/api',
    name: 'ApiTest',
    component: ApiTest
  }
]
```

## 旧API兼容层

保留了与原有API接口的兼容性:

- `/api/analyze`: 图像分析接口
- `/api/v1/chat/completions`: 聊天完成接口
- `/api/search`: 知识库搜索接口
- `/api/status`: 服务状态接口

## 部署说明

### 前端构建

1. 进入前端目录:
   ```
   cd admin_system/frontend
   ```

2. 安装依赖:
   ```
   npm install
   ```

3. 构建生产版本:
   ```
   npm run build
   ```

生成的文件将输出到Django静态文件目录，可直接部署。

### 后端部署

1. 更新依赖:
   ```
   pip install -r requirements.txt
   ```

2. 应用数据库迁移:
   ```
   python manage.py migrate
   ```

3. 收集静态文件:
   ```
   python manage.py collectstatic
   ```

4. 启动服务:
   ```
   python manage.py runserver
   ```

## 使用指南

### 提示词模板管理

1. 访问`/management/vue/#/prompts`打开提示词模板管理界面
2. 选择类别和类型编辑对应模板
3. 使用批量操作功能进行批量更新或重置

### 知识库管理

1. 访问`/management/vue/#/knowledge`打开知识库管理界面
2. 上传或导入知识库文件
3. 查看内容或进行向量化操作

### API测试

1. 访问`/management/vue/#/api`打开API测试界面
2. 选择API接口进行测试
3. 查看响应结果和响应时间

## 后续工作

1. 添加单元测试和集成测试
2. 改进用户体验和界面设计
3. 实现更多高级功能:
   - 批量数据导入/导出
   - 更详细的知识库统计分析
   - 更灵活的提示词模板变量
4. 性能优化和缓存策略改进 