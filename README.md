# AI图像分析辅助设计工具

这是一个基于通义千问VL多模态大模型的图像分析与设计辅助工具，支持图像内容理解、目标检测与边界框显示等功能。系统已与Django Admin管理系统整合，提供统一的管理界面和API接口。

## 主要功能

1. **图像内容分析**：上传图片，AI自动识别图像内容并进行详细描述
2. **目标检测**：支持检测图像中的特定对象并返回边界框坐标
3. **多目标识别**：同时识别图像中的多个对象并标记
4. **边界框可视化**：将检测到的对象用边界框标记并生成可视化图像
5. **支持中文交互**：完全支持中文自然语言交互和分析结果
6. **GPU加速**：支持CUDA GPU加速，大幅提升处理速度
7. **统一管理界面**：Django Admin管理系统，提供可视化的管理和配置界面
8. **知识库管理**：支持导入、编辑和检索设计规范等知识文档
9. **模型配置管理**：可在管理界面中配置和切换不同的AI模型
10. **服务监控**：实时监控系统资源使用情况，包括CPU、内存和GPU

## 系统架构

系统由以下主要组件构成：

- **Django管理系统**：提供整体管理界面、用户认证和权限控制
- **GPU模型服务**：负责AI图像分析的核心功能，基于Qwen-VL模型
- **API兼容层**：确保兼容旧版API，支持现有前端继续使用
- **知识库和向量搜索**：提供高效的知识检索功能
- **WebSocket服务**：支持实时交互式图像分析

## 技术栈

- **后端**：Django + Channels + FastAPI
- **AI模型**：通义千问Qwen-VL多模态大模型
- **图像处理**：PIL库
- **向量检索**：FAISS + SentenceTransformers
- **部署环境**：支持GPU加速的服务器环境

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