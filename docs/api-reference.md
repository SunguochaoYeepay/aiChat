# API 参考文档

本文档提供了设计助手项目REST API的详细说明。所有API端点均需要认证，支持基本认证和会话认证。

## 基础信息

- **基础URL**: `/api/v1/`
- **认证**: 
  - 会话认证 (基于Cookie)
  - 基本认证 (用户名/密码)
  - API密钥 (通过 `X-API-Key` 请求头)
- **响应格式**: JSON

## 提示词模板 API

### 获取所有提示词模板

- **URL**: `/api/v1/templates/`
- **方法**: `GET`
- **描述**: 获取所有提示词模板
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "chat.general",
      "description": "chat类别的general提示词模板",
      "content": "你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}",
      "created_at": "2023-05-10T08:30:00Z",
      "updated_at": "2023-05-10T08:30:00Z"
    },
    // ...
  ]
  ```

### 获取单个提示词模板

- **URL**: `/api/v1/templates/{id}/`
- **方法**: `GET`
- **描述**: 获取指定ID的提示词模板
- **URL参数**:
  - `id` (必须): 提示词模板ID
- **响应**:
  ```json
  {
    "id": 1,
    "name": "chat.general",
    "description": "chat类别的general提示词模板",
    "content": "你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}",
    "created_at": "2023-05-10T08:30:00Z",
    "updated_at": "2023-05-10T08:30:00Z"
  }
  ```

### 创建提示词模板

- **URL**: `/api/v1/templates/`
- **方法**: `POST`
- **描述**: 创建新的提示词模板
- **请求体**:
  ```json
  {
    "name": "chat.new_type",
    "description": "新的提示词模板",
    "content": "你是一个专业的AI助手，请以友好的语气回答问题。\n\n问题: {query}\n\n历史对话: {history}"
  }
  ```
- **响应**:
  ```json
  {
    "id": 5,
    "name": "chat.new_type",
    "description": "新的提示词模板",
    "content": "你是一个专业的AI助手，请以友好的语气回答问题。\n\n问题: {query}\n\n历史对话: {history}",
    "created_at": "2023-06-15T10:25:30Z",
    "updated_at": "2023-06-15T10:25:30Z"
  }
  ```

### 更新提示词模板

- **URL**: `/api/v1/templates/{id}/`
- **方法**: `PUT` 或 `PATCH`
- **描述**: 更新指定ID的提示词模板
- **URL参数**:
  - `id` (必须): 提示词模板ID
- **请求体**:
  ```json
  {
    "name": "chat.general",
    "description": "更新后的描述",
    "content": "你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "name": "chat.general",
    "description": "更新后的描述",
    "content": "你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}",
    "created_at": "2023-05-10T08:30:00Z",
    "updated_at": "2023-06-15T11:20:15Z"
  }
  ```

### 删除提示词模板

- **URL**: `/api/v1/templates/{id}/`
- **方法**: `DELETE`
- **描述**: 删除指定ID的提示词模板
- **URL参数**:
  - `id` (必须): 提示词模板ID
- **响应**: 204 No Content

### 获取提示词模板分类

- **URL**: `/api/v1/templates/categories/`
- **方法**: `GET`
- **描述**: 获取所有提示词模板按分类分组
- **响应**:
  ```json
  [
    {
      "category": "chat",
      "types": {
        "general": "你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}",
        "creative": "你是一个创意写作助手，请用生动的语言回答问题。\n\n用户问题: {query}\n\n历史对话: {history}"
      }
    },
    {
      "category": "search",
      "types": {
        "general": "请基于以下知识回答问题:\n\n{content}\n\n问题: {query}",
        "expert": "作为专家，请基于以下知识提供专业详细的回答:\n\n{content}\n\n问题: {query}"
      }
    }
  ]
  ```

### 刷新提示词模板缓存

- **URL**: `/api/v1/templates/refresh_cache/`
- **方法**: `POST`
- **描述**: 刷新提示词模板缓存
- **响应**:
  ```json
  {
    "status": "success",
    "message": "提示词模板缓存已刷新"
  }
  ```

### 重置提示词模板

- **URL**: `/api/v1/templates/reset/`
- **方法**: `POST`
- **描述**: 将所有提示词模板重置为默认值
- **响应**:
  ```json
  {
    "status": "success",
    "message": "提示词模板已重置为默认值"
  }
  ```

### 批量更新提示词模板

- **URL**: `/api/v1/templates/batch_update/`
- **方法**: `POST`
- **描述**: 批量更新提示词模板
- **请求体**:
  ```json
  {
    "chat": {
      "general": "你是一个AI助手，请回答用户的问题。\n\n用户问题: {query}\n\n历史对话: {history}",
      "creative": "你是一个创意写作助手，请用生动的语言回答问题。\n\n用户问题: {query}\n\n历史对话: {history}"
    },
    "search": {
      "general": "请基于以下知识回答问题:\n\n{content}\n\n问题: {query}"
    }
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "message": "提示词模板保存成功"
  }
  ```

## 知识库 API

### 获取所有知识库

- **URL**: `/api/v1/knowledge/`
- **方法**: `GET`
- **描述**: 获取所有知识库
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "产品手册",
      "description": "产品手册知识库文档",
      "file_path": "knowledge_base/产品手册.md",
      "document_count": 5,
      "is_indexed": true,
      "embedding_model": "text-embedding-ada-002",
      "created_at": "2023-05-10T08:30:00Z",
      "updated_at": "2023-05-10T08:30:00Z"
    },
    // ...
  ]
  ```

### 获取单个知识库

- **URL**: `/api/v1/knowledge/{id}/`
- **方法**: `GET`
- **描述**: 获取指定ID的知识库
- **URL参数**:
  - `id` (必须): 知识库ID
- **响应**:
  ```json
  {
    "id": 1,
    "name": "产品手册",
    "description": "产品手册知识库文档",
    "file_path": "knowledge_base/产品手册.md",
    "content": "# 产品手册\n\n## 简介\n这是一个示例产品手册...",
    "document_count": 5,
    "is_indexed": true,
    "embedding_model": "text-embedding-ada-002",
    "created_at": "2023-05-10T08:30:00Z",
    "updated_at": "2023-05-10T08:30:00Z"
  }
  ```

### 创建知识库

- **URL**: `/api/v1/knowledge/`
- **方法**: `POST`
- **描述**: 创建新的知识库
- **请求体**:
  ```json
  {
    "name": "用户指南",
    "description": "系统用户指南文档",
    "content": "# 用户指南\n\n## 开始使用\n本系统提供了丰富的功能..."
  }
  ```
- **响应**:
  ```json
  {
    "id": 3,
    "name": "用户指南",
    "description": "系统用户指南文档",
    "file_path": null,
    "content": "# 用户指南\n\n## 开始使用\n本系统提供了丰富的功能...",
    "document_count": 0,
    "is_indexed": false,
    "embedding_model": "text-embedding-ada-002",
    "created_at": "2023-06-15T14:30:00Z",
    "updated_at": "2023-06-15T14:30:00Z"
  }
  ```

### 更新知识库

- **URL**: `/api/v1/knowledge/{id}/`
- **方法**: `PUT` 或 `PATCH`
- **描述**: 更新指定ID的知识库
- **URL参数**:
  - `id` (必须): 知识库ID
- **请求体**:
  ```json
  {
    "name": "产品手册V2",
    "description": "更新后的产品手册",
    "content": "# 产品手册V2\n\n## 简介\n这是更新后的产品手册..."
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "name": "产品手册V2",
    "description": "更新后的产品手册",
    "file_path": "knowledge_base/产品手册.md",
    "content": "# 产品手册V2\n\n## 简介\n这是更新后的产品手册...",
    "document_count": 5,
    "is_indexed": true,
    "embedding_model": "text-embedding-ada-002",
    "created_at": "2023-05-10T08:30:00Z",
    "updated_at": "2023-06-15T15:45:30Z"
  }
  ```

### 删除知识库

- **URL**: `/api/v1/knowledge/{id}/`
- **方法**: `DELETE`
- **描述**: 删除指定ID的知识库
- **URL参数**:
  - `id` (必须): 知识库ID
- **响应**: 204 No Content

### 从目录导入知识库

- **URL**: `/api/v1/knowledge/import_directory/`
- **方法**: `POST`
- **描述**: 从目录导入知识库文件
- **请求体**:
  ```json
  {
    "directory": "D:/知识库文档"
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "message": "成功导入3个知识库文档"
  }
  ```

### 上传知识库文件

- **URL**: `/api/v1/knowledge/upload/`
- **方法**: `POST`
- **描述**: 上传知识库文件
- **请求体**: 使用 `multipart/form-data` 格式
  - `file`: 文件数据
- **响应**:
  ```json
  {
    "status": "success",
    "message": "知识库文档 设计规范 上传成功",
    "id": 4
  }
  ```

### 向量化知识库

- **URL**: `/api/v1/knowledge/{id}/index/`
- **方法**: `POST`
- **描述**: 向量化指定ID的知识库
- **URL参数**:
  - `id` (必须): 知识库ID
- **响应**:
  ```json
  {
    "status": "success",
    "message": "知识库向量化成功"
  }
  ```

## 仪表盘 API

### 获取仪表盘统计数据

- **URL**: `/api/v1/dashboard/statistics/`
- **方法**: `GET`
- **描述**: 获取仪表盘统计数据，包括提示词模板、知识库、API调用和系统状态等统计信息
- **响应**:
  ```json
  {
    "template_count": 15,
    "category_count": 4,
    "knowledge_base_count": 8,
    "document_count": 45,
    "system_status": {
      "model_status": "running",
      "api_status": "running"
    },
    "api_calls": {
      "today": 128,
      "total": 5763
    },
    "recent_activities": [
      {
        "title": "更新了聊天提示词模板",
        "time": "2023-12-15 14:30",
        "type": "template"
      },
      {
        "title": "添加了新的知识库文档",
        "time": "2023-12-15 11:20",
        "type": "knowledge"
      }
    ],
    "prompt_usage": {
      "chat": 45,
      "search": 30,
      "image_analysis": 15,
      "topic_matching": 10
    }
  }
  ```

## API 元数据

### 获取API端点列表

- **URL**: `/api/v1/endpoints`
- **方法**: `GET`
- **描述**: 获取所有可用的API端点信息
- **响应**:
  ```json
  {
    "endpoints": [
      {
        "id": 1,
        "name": "聊天完成",
        "path": "/api/v1/chat/completions",
        "method": "POST",
        "description": "发送消息到模型并获取聊天回复",
        "request_schema": {
          "messages": [
            {"role": "system", "content": "你是一个AI助手"},
            {"role": "user", "content": "你好，请介绍一下自己"}
          ],
          "stream": false,
          "template_type": "general"
        }
      },
      // ...
    ]
  }
  ```

### 获取API密钥列表

- **URL**: `/api/v1/api-keys`
- **方法**: `GET`
- **描述**: 获取所有API密钥信息(部分敏感信息会被隐藏)
- **响应**:
  ```json
  {
    "api_keys": [
      {
        "id": 1,
        "name": "默认密钥",
        "key": "sk-demo...1234",
        "created_at": "2023-05-10T08:30:00",
        "is_active": true
      },
      // ...
    ]
  }
  ```

## 旧API兼容层

以下API端点保持与原有系统的兼容性：

### 聊天完成

- **URL**: `/api/v1/chat/completions`
- **方法**: `POST`
- **描述**: 发送消息到模型并获取回复
- **请求体**:
  ```json
  {
    "messages": [
      {"role": "system", "content": "你是一个AI助手"},
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "stream": false,
    "template_type": "general",
    "knowledge_search": true
  }
  ```
- **响应**:
  ```json
  {
    "id": "chatcmpl-123456789",
    "object": "chat.completion",
    "created": 1677858242,
    "model": "gpt-3.5-turbo-0613",
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "你好！我是一个AI助手，由人工智能技术驱动..."
        },
        "finish_reason": "stop",
        "index": 0
      }
    ]
  }
  ```

### 图像分析

- **URL**: `/api/analyze`
- **方法**: `POST`
- **描述**: 分析图像并获取描述
- **请求体**:
  ```json
  {
    "image_base64": "...(base64编码的图像数据)...",
    "query": "描述这张图片",
    "template_type": "general"
  }
  ```
- **响应**:
  ```json
  {
    "text": "这是一张海滩风景照片，蓝色的海洋和金色的沙滩相互辉映...",
    "model": "Qwen-VL"
  }
  ```

### 知识库搜索

- **URL**: `/api/search`
- **方法**: `POST`
- **描述**: 在知识库中搜索相关内容
- **请求体**:
  ```json
  {
    "query": "如何使用知识库搜索功能?",
    "top_k": 3
  }
  ```
- **响应**:
  ```json
  {
    "results": [
      {
        "id": 1,
        "name": "用户指南",
        "content": "## 知识库搜索功能\n知识库搜索功能允许用户通过关键词查询相关文档...",
        "similarity": 0.85
      },
      // ...
    ],
    "count": 3
  }
  ```

### 服务状态

- **URL**: `/api/status`
- **方法**: `GET`
- **描述**: 获取服务的当前状态
- **响应**:
  ```json
  {
    "status": "running",
    "model_loaded": true,
    "model_name": "Qwen-VL-Chat-Int4",
    "uptime": "2d 5h 30m",
    "gpu_memory": "4.2 GB / 8.0 GB"
  }
  ``` 