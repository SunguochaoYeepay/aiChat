## Quick Start Guide

**Two simple startup scripts are provided:**

1. **start_admin.bat** - Start Admin System
   - URL: http://localhost:8000/admin/
   - For: Managing knowledge base, model settings, etc.

2. **start_api.bat** - Start API Service (with model loading)
   - URL: http://localhost:8001/api/
   - For: AI conversation and image analysis API
   - Note: First startup takes a few minutes for model loading

---

# Qwen-VL-Chat Service

# AI图像分析与管理系统

基于Django和先进视觉语言模型的一体化图像分析与内容管理系统。

## 系统概述

本系统是一个集图像分析、知识库管理和管理界面于一体的综合性平台，主要功能包括：

1. **图像内容分析**：自动识别和分析图像内容
2. **目标检测**：识别图像中的对象并显示边界框
3. **知识库搜索**：基于向量搜索的智能知识库查询
4. **多模态对话**：支持图文混合的交互式对话
5. **模型配置管理**：通过管理界面轻松管理模型配置
6. **完整的管理后台**：直观的Web界面管理系统各项功能

## 系统架构

系统采用了Django框架作为基础，整合了原有的FastAPI图像分析服务，形成一个统一的应用。
主要组件包括：

- **核心服务模块**：处理图像分析、文本处理等核心功能
- **API兼容层**：保持与原有系统相同的API接口，确保现有前端正常工作
- **管理界面**：提供直观的Web界面管理系统
- **数据库存储**：使用SQLite数据库存储知识库和配置信息
- **WebSocket支持**：提供实时通信功能

## 项目结构

```
design-helper/
├── admin_system/          # Django后端服务
├── chat_env/              # Python虚拟环境目录
├── docs/                  # 文档目录
│   ├── readme/            # 多语言说明文档
│   └── 启动说明.md         # 启动说明文档
├── logs/                  # 日志文件
├── scripts/               # 脚本目录
│   ├── launchers/         # 各种启动脚本
│   ├── patches/           # 补丁文件
│   ├── startup/           # 启动核心脚本
│   └── tests/             # 测试脚本
├── start.bat              # 中文主启动脚本
├── start_en.bat           # 英文主启动脚本
└── README.md              # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.8+
- CUDA支持的GPU (推荐，但不强制)
- 至少8GB内存，推荐16GB或更多

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

本系统提供了简化的启动方式：

#### 主启动脚本

- `start.bat` - 中文主启动脚本
- `start_en.bat` - 英文主启动脚本

只需双击运行任一启动脚本，即可进入启动器界面。

#### 启动器

如果您想直接访问启动器，可以在`scripts/launchers`目录中找到：
- `start_launcher.bat` - 中文界面启动器
- `launcher.bat` - 英文界面启动器

#### 推荐启动方式（一键启动）

在启动器中选择推荐的启动方式：
- `start_all_services.bat`（中文界面）或 `start_simple.bat`（英文界面）
- 建议选择**完整启动**选项以获得最佳体验

> 详细说明请参阅 `docs/启动说明.md` 文件

#### 命令行启动（高级用户）

也可以直接使用命令行启动服务：

```bash
cd admin_system
python manage.py runserver 0.0.0.0:8000 --settings=admin_system.minimal_settings
```

启动后，可以通过以下地址访问系统：

- 管理界面：http://127.0.0.1:8000/admin/
- API接口：http://127.0.0.1:8000/api/status (状态检查)
- 聊天API：http://127.0.0.1:8000/api/v1/chat/completions

### API接口

系统提供以下API接口：

- **GET /api/status** - 获取服务状态
- **POST /api/search** - 知识库搜索
- **POST /api/v1/chat/completions** - 聊天完成
- **POST /api/analyze** - 图像分析
- **WebSocket /ws/chat** - 聊天WebSocket接口
- **WebSocket /ws/analyze** - 图像分析WebSocket接口

## 管理功能

系统提供了完善的管理功能，可以通过管理界面进行：

- 模型配置管理
- 知识库管理
- 提示词模板管理
- 服务状态监控

## 技术栈

- Django：Web框架
- Channels：WebSocket支持
- PyTorch & transformers：深度学习框架
- SQLite：数据库
- 向量检索：知识库搜索

## 安装指南

### 系统要求

- Python 3.8+
- CUDA 11.7+（GPU加速）
- 至少10GB GPU显存（推荐16GB+）
- 8GB+ 系统内存
- 30GB+ 磁盘空间（包括模型）

### 依赖安装

```bash
# 安装GPU服务依赖
pip install -r requirements.txt

# 安装Django管理系统依赖
pip install -r admin_system/requirements.txt

# 安装监控工具依赖
pip install matplotlib pynvml
```

### 模型配置

需要预先下载通义千问Qwen-VL-Chat-Int4模型到本地：
- 默认模型路径：`D:/AI-DEV/models/Qwen-VL-Chat-Int4`
- 如需修改模型路径，可在管理界面中配置

### 初始化管理系统

```bash
cd admin_system
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## 使用方法

### 统一启动服务

使用新的统一启动脚本可以同时启动Django管理系统和GPU模型服务：

```bash
# 启动所有服务
python start_service.py --all

# 仅启动Django管理系统
python start_service.py --django

# 仅启动GPU模型服务
python start_service.py --gpu
```

### 服务监控

系统提供实时监控工具，用于监控服务性能和状态：

```bash
# 默认监控（5秒间隔）
python monitor_service.py

# 指定间隔时间（秒）
python monitor_service.py --interval 10

# 监控特定时长（分钟）然后自动生成报告
python monitor_service.py --duration 3600

# 将监控数据保存到日志文件
python monitor_service.py --log
```

监控工具会生成资源使用情况图表，保存在`logs/charts/`目录下。

### 管理界面访问

Django管理系统运行在：http://localhost:8000/admin

使用创建的超级用户账号登录系统。

### API接口

系统提供以下API接口：

1. **图像分析 API**：`POST /api/analyze`
   - 请求体：`{"image_base64": "<base64编码的图像>", "query": "这张图片是什么?"}`
   - 返回：`{"result": "分析结果", "processing_time": "处理时间", "boxed_image_url": "边界框图像URL"}`

2. **聊天 API**：`POST /api/chat/completions`
   - 请求体：`{"messages": [{"role": "user", "content": "问题内容"}]}`
   - 返回：聊天响应

3. **知识库检索 API**：`POST /api/search`
   - 请求体：`{"topic": "话题名称", "query": "相关问题"}`
   - 返回：知识库中的相关回答

4. **服务状态 API**：`GET /api/status`
   - 返回服务状态信息和GPU使用情况

### WebSocket接口

系统支持WebSocket实时交互：

1. **聊天 WebSocket**：`ws://localhost:8000/ws/chat`
2. **图像分析 WebSocket**：`ws://localhost:8000/ws/analyze`

## 系统管理

### 知识库管理

在Django管理界面中，可以进行以下操作：

1. 添加新的知识文档
2. 编辑现有知识库内容
3. 处理知识库向量索引
4. 测试知识库检索效果

### 模型配置

可以在管理界面中配置和管理模型：

1. 添加新的模型配置
2. 设置模型参数（精度、批处理大小等）
3. 切换当前使用的模型
4. 重新加载模型

### 服务控制

管理界面提供服务控制功能：

1. 启动/停止GPU服务
2. 查看服务运行状态
3. 监控资源使用情况

## 目录结构

- `gpu_model_server.py`：GPU模型服务主程序
- `admin_system/`：Django管理系统
  - `manage.py`：Django管理命令
  - `api/`：API兼容层
  - `core/`：核心服务功能
  - `management/`：系统管理界面
  - `vector_search/`：向量检索功能
  - `knowledge_base/`：知识库服务
- `start_service.py`：统一启动脚本
- `monitor_service.py`：服务监控工具
- `static/`：静态文件目录
- `knowledge_base/`：知识库文档目录
- `requirements.txt`：GPU服务依赖项列表

## 故障排除

### 常见问题

1. **服务无法启动**
   - 检查端口占用情况：`netstat -ano | findstr 8000`
   - 检查GPU是否可用：`python -c "import torch; print(torch.cuda.is_available())"`

2. **GPU内存不足**
   - 使用监控工具查看GPU内存使用情况
   - 在管理界面中调整模型批处理大小或精度

3. **API请求超时**
   - 增加请求超时时间
   - 检查服务器负载状态
   - 使用监控工具排查性能瓶颈

### 日志文件

系统日志文件位于：
- GPU服务日志：`gpu_server_log.txt`
- Django服务日志：`admin_system/logs/django.log`
- 监控日志：`logs/monitor_*.log`

## 开发与扩展

### 添加新模型

1. 在管理界面中添加新的模型配置
2. 在核心服务中实现相应的模型加载逻辑
3. 重启服务以应用更改

### 扩展API功能

1. 在`api/views.py`中添加新的API端点
2. 在`api/urls.py`中注册URL路由
3. 实现对应的核心功能

## 许可证

MIT 

## 系统更新说明

系统已完成整合，将原有的FastAPI图像分析服务完全集成到Django管理系统中。主要改进包括：

1. **统一管理界面**: 通过Django Admin提供所有功能的集中管理
2. **核心功能整合**: 图像分析、知识库管理、模型配置等功能现在完全集成
3. **API接口兼容**: 保持与原有系统相同的API接口，确保现有前端正常工作
4. **WebSocket支持**: 通过Django Channels提供实时通信功能
5. **部署脚本**: 提供部署脚本，简化生产环境部署过程

### 系统清理

以下为系统清理工作：

1. **移除旧服务**：已移除独立的FastAPI服务，功能已集成到新系统
2. **移除调试工具**：生产环境中已移除Django Debug Toolbar
3. **优化配置**：更新了SECRET_KEY，关闭了DEBUG模式，为生产环境做好准备
4. **添加部署脚本**：提供`deploy_production.py`脚本，简化生产环境部署

### 部署说明

要部署系统到生产环境，请执行以下步骤：

1. 安装依赖：
   ```bash
   pip install -r admin_system/requirements.txt
   ```

2. 运行部署脚本：
   ```bash
   cd admin_system
   python deploy_production.py
   ```

3. 使用生产服务器启动应用：
   ```bash
   # 使用Gunicorn（HTTP）
   gunicorn admin_system.wsgi:application --bind 0.0.0.0:8000
   
   # 或使用Daphne（HTTP + WebSocket）
   daphne admin_system.asgi:application -b 0.0.0.0 -p 8000
   ```

4. 或者使用开发服务器（不推荐用于生产）：
   ```bash
   cd admin_system
   python manage.py runserver 0.0.0.0:8000
   ``` 

# Qwen-VL-Chat API 服务

这个项目提供了一个基于Django的API服务，用于与Qwen-VL-Chat模型交互。

## 系统需求

- Windows 10/11
- Python 3.9+
- CUDA支持的NVIDIA GPU (至少8GB显存)
- 已下载的Qwen-VL-Chat-Int4模型

## 项目结构

```
design-helper/
├── admin_system/          # Django后端服务
├── chat_env/              # Python虚拟环境目录
├── docs/                  # 文档目录
│   ├── readme/            # 多语言说明文档
│   └── 启动说明.md         # 启动说明文档
├── logs/                  # 日志文件
├── scripts/               # 脚本目录
│   ├── launchers/         # 各种启动脚本
│   ├── patches/           # 补丁文件
│   ├── startup/           # 启动核心脚本
│   └── tests/             # 测试脚本
├── start.bat              # 中文主启动脚本
├── start_en.bat           # 英文主启动脚本
└── README.md              # 项目说明文档
```

## 快速开始

1. 确保您已安装Python 3.9+和CUDA支持
2. 确保您已下载Qwen-VL-Chat-Int4模型到`D:/AI-DEV/models/Qwen-VL-Chat-Int4`目录
   - 如果您的模型在其他位置，请修改`scripts/startup/startup.py`文件中的`model_path`变量
3. 双击项目根目录下的`start_service.bat`启动服务
4. 服务器将自动加载模型并启动API服务

## API使用方法

### 聊天API

**端点**: `http://localhost:8000/api/v1/chat/completions`

**方法**: POST

**请求体**:
```json
{
  "messages": [
    {"role": "system", "content": "你是一个有用的助手。"},
    {"role": "user", "content": "你好，请介绍一下自己。"}
  ],
  "stream": false
}
```

**响应**:
```json
{
  "id": "chatcmpl-123456789",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "qwen-vl-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "我是通义千问，一个由阿里云开发的大型语言模型..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "processing_time": "2.5秒"
}
```

## 测试指南

系统提供了完整的测试用例，覆盖所有API接口：

1. **运行完整测试**
   ```bash
   # 运行所有测试，包括聊天、图像分析和WebSocket测试
   scripts\test_scripts\run_all_tests.bat
   ```

2. **运行单项测试**
   ```bash
   # 测试聊天API
   python scripts/test_scripts/test_chat_api.py
   
   # 测试图像分析API
   python scripts/test_scripts/test_analyze_api.py
   
   # 测试WebSocket接口
   python scripts/test_scripts/test_websocket.py
   ```

3. **安装测试依赖**
   ```bash
   pip install -r scripts/test_scripts/test_requirements.txt
   ```

测试用例详情:
- `test_chat_api.py`: 测试聊天完成API (`/api/v1/chat/completions`)
- `test_analyze_api.py`: 测试图像分析API (`/api/analyze`)
- `test_websocket.py`: 测试WebSocket接口 (`ws://server/ws/chat/` 和 `ws://server/ws/analyze/`)
- `check_model_status.py`: 检查模型加载状态

测试结果会以日志形式输出，并通过退出码指示测试成功与否（0表示成功，非0表示失败）。

## 常见问题

- **问题**: 启动时显示"模型未加载"
  **解决方案**: 确保模型路径正确，且您的GPU有足够显存

- **问题**: 无法启动Django服务器
  **解决方案**: 确保已正确安装所有依赖项，并且端口8000未被占用

- **问题**: API返回错误
  **解决方案**: 检查请求格式是否符合要求，确保模型已成功加载

## 依赖项

- Django 4.2+
- PyTorch (CUDA支持版本)
- transformers
- auto-gptq
- optimum 

# 系统优化说明

## 最近的优化内容

最近我们对系统进行了一系列优化，特别是解决了"模型未加载"的问题：

### 1. 模型服务模块优化
- 添加了线程锁防止并发加载模型
- 增加了模型测试功能确保加载成功
- 增强了错误处理和日志记录
- 添加了模型加载状态检查

### 2. API服务优化
- 改进了处理模型未加载情况的逻辑
- 增加了详细日志记录
- 优化了错误消息

### 3. 启动脚本优化
- 添加了等待模型加载完成的机制
- 增加了模型加载验证步骤
- 使用标准日志替代简单的print输出

### 4. 测试脚本优化
- 增加了重试机制
- 添加了服务状态检查
- 提供了更详细的错误信息和日志

## 如何使用

使用以下方法启动和测试系统：

1. 运行 `run_test.bat` 脚本，这将启动服务并自动测试API
2. 或者分步执行：
   - `python scripts/startup/load_model_and_run_django.py` 启动服务
   - `python scripts/test_scripts/test_chat_api.py` 测试API

## 常见问题排查

如果遇到问题，请检查：

1. 查看 `model_startup.log` 日志文件了解模型加载状态
2. 确认模型路径 `D:/AI-DEV/models/Qwen-VL-Chat-Int4` 是否正确
3. 检查GPU是否可用和显存是否充足
4. 查看Django服务是否正常启动在8000端口

## 后续优化方向

1. 实现更健壮的模型加载机制
2. 添加模型加载进度反馈
3. 优化内存使用
4. 增加更完善的监控和自我恢复机制 

## API接口文档

系统提供以下对外服务接口：

### HTTP接口

| 接口路径 | 方法 | 描述 |
|---------|------|------|
| `/api/analyze` | POST | 图像分析接口，接收图像和查询文本，返回分析结果 |
| `/api/v1/chat/completions` | POST | 聊天完成接口，兼容OpenAI格式，支持流式响应 |
| `/api/search` | POST | 知识库搜索接口，根据查询文本返回相关知识条目 |
| `/api/status` | GET | 服务状态接口，返回系统和模型的当前状态 |

### WebSocket接口

系统还提供以下WebSocket接口，用于实时通信：

| 接口 | 描述 |
|------|------|
| `ws://服务器地址/ws/chat/` | 聊天WebSocket接口，支持实时对话 |
| `ws://服务器地址/ws/analyze/` | 图像分析WebSocket接口，支持实时图像分析 |

### 接口使用示例

#### 图像分析接口
```json
// POST /api/analyze
{
  "image_base64": "图像的base64编码",
  "query": "关于图像的问题"
}
```

#### 聊天完成接口
```json
// POST /api/v1/chat/completions
{
  "messages": [
    {"role": "user", "content": "用户问题"}
  ],
  "stream": false
}
```

#### 知识库搜索接口
```json
// POST /api/search
{
  "query": "搜索关键词",
  "top_k": 5
}
``` 