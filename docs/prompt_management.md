# 提示词管理系统

## 背景与目标

之前的系统中，提示词模板直接硬编码在代码中，存在以下问题：

1. 缺乏灵活性：修改提示词需要修改代码
2. 难以维护：提示词分散在代码的不同位置
3. 不便于优化：无法方便地进行A/B测试
4. 不适合非技术人员调整：产品经理、设计师等无法直接调整提示词

为解决以上问题，我们实现了提示词管理系统，将提示词从代码中分离出来，实现外部配置和动态管理。

## 实现方案

### 1. 提示词模板配置文件

我们使用JSON格式的配置文件存储提示词模板：

```
config/prompt_templates.json
```

### 2. 提示词管理模块

创建了专门的提示词管理模块`prompt_manager.py`，负责：

- 加载和解析提示词模板
- 判断查询是否与设计相关
- 查找最合适的知识库主题
- 动态构建提示词

### 3. 提示词模板编辑器

提供了Web界面用于在线编辑提示词模板：

```
http://localhost:8000/static/prompt_editor.html
```

### 4. 提示词管理API

增加了以下API端点用于管理提示词模板：

- `GET /prompt_templates` - 获取所有提示词模板
- `POST /prompt_templates` - 更新提示词模板
- `POST /refresh_templates` - 刷新提示词模板

## 模板结构

提示词模板按照功能分为以下几类：

1. **chat**：文本聊天类提示词
   - knowledge_base：使用知识库内容的提示词模板
   - general：通用提示词模板

2. **image_analysis**：图像分析类提示词
   - knowledge_base：使用知识库内容的提示词模板
   - general：通用提示词模板
   - design_evaluation：设计评估专用提示词模板

3. **search**：知识库搜索类提示词
   - knowledge_base：使用知识库内容的提示词模板

4. **topic_matching**：主题匹配配置
   - score_weights：不同匹配规则的权重配置

## 使用方法

### 管理提示词模板

1. 访问提示词模板编辑器：`http://localhost:8000/static/prompt_editor.html`
2. 选择需要编辑的模板类别和类型
3. 修改模板内容
4. 点击"保存"按钮保存更改

### 在代码中使用

```python
from app.prompt_manager import prompt_manager

# 判断查询是否与设计相关
is_design_query = prompt_manager.is_design_query(query)

# 查找最合适的知识库主题
best_topic = prompt_manager.find_best_topic(query, topics)

# 构建提示词
prompt = prompt_manager.build_prompt("chat", query, content, topic)
```

## 注意事项

1. 提示词模板中可使用以下变量：
   - `{query}`：用户查询内容
   - `{content}`：知识库内容
   - `{topic}`：知识库主题

2. 修改模板后无需重启服务，系统会自动加载最新的模板

3. 如果模板配置文件不存在或格式错误，系统会自动创建默认配置 