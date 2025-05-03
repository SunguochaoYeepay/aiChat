# AI图像分析辅助设计工具

这是一个基于通义千问VL多模态大模型的图像分析与设计辅助工具，支持图像内容理解、目标检测与边界框显示等功能。

## 主要功能

1. **图像内容分析**：上传图片，AI自动识别图像内容并进行详细描述
2. **目标检测**：支持检测图像中的特定对象并返回边界框坐标
3. **多目标识别**：同时识别图像中的多个对象并标记
4. **边界框可视化**：将检测到的对象用边界框标记并生成可视化图像
5. **支持中文交互**：完全支持中文自然语言交互和分析结果
6. **GPU加速**：支持CUDA GPU加速，大幅提升处理速度

## 技术栈

- **后端**：FastAPI + Python
- **AI模型**：通义千问Qwen-VL多模态大模型
- **图像处理**：PIL库
- **部署环境**：支持GPU加速

## 环境配置

### 依赖安装

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装GPU支持所需的额外依赖
pip install optimum auto-gptq
```

### 模型配置

需要预先下载通义千问Qwen-VL-Chat-Int4模型到本地：
- 默认模型路径：`D:/AI-DEV/models/Qwen-VL-Chat-Int4`
- 如需修改模型路径，请在`gpu_model_server.py`中更新`model_id`变量

## 使用方法

### 服务端启动

**方法1**：使用简易启动脚本
```bash
start_gpu.bat
```

**方法2**：使用带日志的启动脚本
```bash
run_gpu_server.bat
```

**方法3**：直接启动
```bash
python gpu_model_server.py
```

服务将在 http://localhost:8000 上启动

### API接口

1. **图像分析 API**：`POST /analyze`
   - 请求体：`{"image_base64": "<base64编码的图像>", "query": "这张图片是什么?"}`
   - 返回：`{"result": "分析结果", "processing_time": "处理时间", "boxed_image_url": "边界框图像URL"}`

2. **聊天 API**：`POST /v1/chat/completions`
   - 请求体：`{"messages": [{"role": "user", "content": "问题内容"}]}`
   - 返回：聊天响应

3. **知识库检索 API**：`POST /search`
   - 请求体：`{"topic": "话题名称", "query": "相关问题"}`
   - 返回：知识库中的相关回答

4. **服务状态 API**：`GET /status`
   - 返回服务状态信息和GPU使用情况

### 测试服务

使用GPU测试脚本：
```bash
python gpu_test.py
```

此脚本会测试GPU环境、服务连接和聊天功能，是验证服务器正常工作的最快方法。

## 目录结构

- `gpu_model_server.py`：主服务器程序
- `start_gpu.bat`：简易启动脚本
- `run_gpu_server.bat`：带日志的详细启动脚本
- `gpu_test.py`：GPU服务测试脚本
- `static/`：静态文件目录
  - `test.html`：测试页面
  - `box_images/`：存储边界框图像的目录
- `knowledge_base/`：知识库目录（用于存储设计规范等文档）
- `app/`：前端应用程序
- `requirements.txt`：依赖项列表
- `SimSun.ttf`：宋体字体文件（用于边界框标签）

## GPU性能注意事项

1. 第一次加载模型会较慢，请耐心等待
2. 使用GPU时，内存占用约为9-10GB（使用RTX 4090测试）
3. 响应时间通常为2-10秒，比CPU版本快5-10倍
4. 如果GPU显存不足，请考虑使用更小的模型或调整batch_size

## 许可证

MIT 