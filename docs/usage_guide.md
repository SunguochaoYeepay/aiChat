# AI图像分析服务使用指南

## 系统概述

AI图像分析服务是一个基于Django和通义千问VL多模态大模型的图像分析与设计辅助工具。系统包含以下核心功能：

1. **图像内容分析**：自动识别和分析图像内容
2. **目标检测**：识别图像中的对象并显示边界框
3. **知识库搜索**：基于向量搜索的智能知识库查询
4. **多模态对话**：支持图文混合的交互式对话

## 部署与安装

### 环境要求

- Python 3.8+ 
- CUDA支持的GPU (推荐，但不强制)
- 至少8GB内存，推荐16GB或更多

### 快速安装

1. 克隆项目代码
   ```bash
   git clone <项目仓库地址>
   cd design-helper/admin_system
   ```

2. 运行部署脚本
   ```bash
   python deploy.py
   ```
   
   此脚本将自动执行以下操作：
   - 检查环境
   - 安装依赖
   - 设置数据库
   - 收集静态文件
   - 创建超级用户

3. 启动开发服务器
   ```bash
   python manage.py runserver
   ```

### 生产环境部署

1. 配置生产环境
   ```bash
   python deploy.py --production
   ```
   
   此命令将生成以下配置文件：
   - `ai-design-helper.service` - systemd服务文件
   - `ai-design-helper.nginx.conf` - Nginx配置文件

2. 安装服务（需要root权限）
   ```bash
   sudo cp ai-design-helper.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable ai-design-helper
   sudo systemctl start ai-design-helper
   ```

3. 配置Nginx（需要root权限）
   ```bash
   sudo cp ai-design-helper.nginx.conf /etc/nginx/sites-available/ai-design-helper
   sudo ln -s /etc/nginx/sites-available/ai-design-helper /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## 系统使用

### 管理界面

1. 访问管理界面
   - 开发环境：http://localhost:8000/admin/
   - 生产环境：http://<your-domain>/admin/

2. 使用超级用户账号登录（默认用户名：admin，密码：admin123）

### 模型管理

1. 在管理界面中找到"模型配置"，可以添加、编辑和删除模型配置
2. 点击"激活"按钮设置当前使用的模型
3. 通过"模型服务状态"页面监控模型运行状态

### 知识库管理

1. 在管理界面中找到"知识库"，可以添加、编辑和删除知识库内容
2. 使用"处理并索引选中的知识库"操作来生成向量索引
3. 通过"向量搜索"页面测试知识库搜索功能

### API调用

#### 图像分析API

- **URL**: `/analyze` 或 `/api/analyze`
- **方法**: POST
- **参数**:
  ```json
  {
    "image_base64": "base64编码的图像",
    "query": "分析请求，如"这张图片中有什么？""
  }
  ```
- **返回**:
  ```json
  {
    "result": "分析结果文本",
    "processing_time": "处理时间",
    "boxed_image_url": "带边界框的图像URL（如果有）"
  }
  ```

#### 聊天API

- **URL**: `/v1/chat/completions` 或 `/api/v1/chat/completions`
- **方法**: POST
- **参数**:
  ```json
  {
    "messages": [
      {"role": "user", "content": "你好，请介绍一下自己"},
      {"role": "assistant", "content": "我是AI助手，请问有什么可以帮助你的？"},
      {"role": "user", "content": "分析这个设计有什么问题"}
    ],
    "stream": false
  }
  ```
- **返回**:
  ```json
  {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677858242,
    "model": "qwen-vl-chat",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "这个设计有以下几个问题..."
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "total_tokens": 0
    }
  }
  ```

#### 知识库搜索API

- **URL**: `/search` 或 `/api/search`
- **方法**: POST
- **参数**:
  ```json
  {
    "query": "搜索关键词",
    "top_k": 5
  }
  ```
- **返回**:
  ```json
  {
    "results": [
      {
        "id": 1,
        "name": "知识库名称",
        "content": "匹配的内容片段",
        "similarity": 0.85
      }
    ],
    "count": 1
  }
  ```

### WebSocket接口

#### 聊天WebSocket

- **URL**: `/ws/chat`
- **消息格式**:
  ```json
  {
    "type": "chat",
    "messages": [{"role": "user", "content": "你好"}]
  }
  ```

#### 图像分析WebSocket

- **URL**: `/ws/analyze`
- **消息格式**:
  ```json
  {
    "type": "analyze",
    "image_base64": "base64编码的图像",
    "query": "分析请求"
  }
  ```

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查模型路径是否正确
   - 确认GPU内存是否足够
   - 尝试使用CPU模式（在模型配置中选择）

2. **知识库搜索无结果**
   - 检查知识库是否已正确索引
   - 尝试使用更通用的关键词
   - 重新处理知识库

3. **WebSocket连接失败**
   - 确认浏览器支持WebSocket
   - 检查防火墙设置
   - 检查Nginx配置是否正确转发WebSocket请求

### 日志查看

- 开发环境日志直接显示在控制台
- 生产环境日志可通过以下命令查看:
  ```bash
  sudo journalctl -u ai-design-helper
  ```

## 系统维护

### 数据库备份

```bash
python manage.py dumpdata > db_backup.json
```

### 恢复数据库

```bash
python manage.py loaddata db_backup.json
```

### 更新模型

1. 在管理界面中添加新的模型配置
2. 激活新模型
3. 在"模型服务状态"页面中点击"重新加载"

## 技术支持

如有问题，请联系系统管理员或提交Issue到项目仓库。 