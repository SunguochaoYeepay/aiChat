# 设计助手后端API接口文档

## 基本信息

- **服务地址**: http://127.0.0.1:8000
- **认证方式**: 无需认证

## HTTP API接口列表

| 接口路径 | 方法 | 描述 |
|---------|------|------|
| `/api/analyze` | POST | 图像分析接口，接收图像和查询文本，返回分析结果 |
| `/api/v1/chat/completions` | POST | 聊天完成接口，兼容OpenAI格式，支持流式响应 |
| `/api/search` | POST | 知识库搜索接口，根据查询文本返回相关知识条目 |
| `/api/status` | GET | 服务状态接口，返回系统和模型的当前状态 |

## 详细API说明

### 1. 图像分析API

分析上传的图像并回答相关问题。

- **URL**: `/api/analyze`
- **方法**: POST
- **Content-Type**: application/json

**请求参数**:

```json
{
  "image_base64": "图像的base64编码",
  "query": "关于图像的问题"
}
```

**返回结果**:

```json
{
  "result": "分析结果文本",
  "processing_time": "处理时间(秒)",
  "boxed_image_url": "带边界框的图像URL（如果有）"
}
```

**示例**:

```javascript
// 前端示例代码
const response = await fetch('http://127.0.0.1:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    image_base64: imageBase64String,
    query: "这张设计图有什么问题？"
  }),
});
const data = await response.json();
```

### 2. 聊天API

与AI助手进行对话，支持多轮对话。

- **URL**: `/api/v1/chat/completions`
- **方法**: POST
- **Content-Type**: application/json

**请求参数**:

```json
{
  "messages": [
    {"role": "user", "content": "第一个问题"},
    {"role": "assistant", "content": "AI的回复"},
    {"role": "user", "content": "后续问题"}
  ],
  "stream": false
}
```

参数说明:
- `messages`: 对话历史记录，包含用户和助手的消息
- `stream`: 是否使用流式返回，设为true时支持实时返回

**返回结果**:

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
        "content": "AI助手的回复内容"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

**示例**:

```javascript
// 前端示例代码
const response = await fetch('http://127.0.0.1:8000/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      {role: "user", content: "分析这个设计的排版有什么问题?"}
    ],
    stream: false
  }),
});
const data = await response.json();
```

### 3. 知识库搜索API

在知识库中搜索相关内容。

- **URL**: `/api/search`
- **方法**: POST
- **Content-Type**: application/json

**请求参数**:

```json
{
  "query": "搜索关键词",
  "top_k": 5
}
```

参数说明:
- `query`: 搜索查询文本
- `top_k`: 返回结果数量，默认为5

**返回结果**:

```json
{
  "results": [
    {
      "content": "搜索到的内容1",
      "score": 0.89,
      "source": "来源文档"
    },
    {
      "content": "搜索到的内容2",
      "score": 0.75,
      "source": "来源文档"
    }
  ],
  "processing_time": "0.12秒"
}
```

**示例**:

```javascript
// 前端示例代码
const response = await fetch('http://127.0.0.1:8000/api/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "设计原则",
    top_k: 3
  }),
});
const data = await response.json();
```

### 4. 服务状态API

获取服务器和模型的当前状态。

- **URL**: `/api/status`
- **方法**: GET

**返回结果**:

```json
{
  "status": "running",
  "model": "qwen-vl-chat",
  "gpu_usage": {
    "memory_used": "4.2 GB",
    "memory_total": "12 GB",
    "utilization": "32%"
  },
  "uptime": "2天13小时45分钟"
}
```

**示例**:

```javascript
// 前端示例代码
const response = await fetch('http://127.0.0.1:8000/api/status');
const data = await response.json();
```

## WebSocket接口

系统支持WebSocket连接，用于实时通信：

| 接口 | 描述 |
|------|------|
| `ws://127.0.0.1:8000/ws/chat/` | 聊天WebSocket接口，支持实时对话 |
| `ws://127.0.0.1:8000/ws/analyze/` | 图像分析WebSocket接口，支持实时图像分析 |

### WebSocket使用示例

```javascript
// 聊天WebSocket示例
const chatSocket = new WebSocket('ws://127.0.0.1:8000/ws/chat/');

chatSocket.onopen = () => {
  console.log('WebSocket连接已建立');
  chatSocket.send(JSON.stringify({
    message: "你好，请分析这个设计",
    type: "message"
  }));
};

chatSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('收到消息:', data);
};
```

## 错误处理

所有API在发生错误时会返回相应的HTTP状态码和错误信息：

```json
{
  "error": "错误描述信息"
}
```

常见错误状态码：
- 400: 请求参数错误
- 404: 请求的资源不存在 