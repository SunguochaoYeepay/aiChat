# AI系统启动说明

## 启动脚本

本系统包含三个启动脚本，根据需要选择使用：

### 1. 启动管理系统

```
start_admin.bat
```

- 启动Django管理后台
- 访问地址：http://localhost:8000/admin/

### 2. 启动API服务

```
start_api.bat
```

- 启动API服务并加载AI模型
- 访问地址：http://localhost:8000/api/
- 聊天接口：http://localhost:8000/api/v1/chat/completions
- 状态查询：http://localhost:8000/api/status

### 3. 后台启动服务

```
start_and_load.bat
```

- 在后台启动服务并自动加载模型
- 关闭脚本窗口后服务仍在运行
- 访问地址同上

## 注意事项

1. 首次启动时模型加载可能需要几分钟，请耐心等待
2. 可以通过访问 http://localhost:8000/api/status 检查模型加载状态
3. 当状态返回 `"model_loaded": true` 时，表示模型已完全加载
4. 如需停止服务，直接关闭相应的命令窗口即可

## 变更日志

### 2023-05-06

#### 增强API管理功能

**新增功能：**

1. **API管理界面**
   - 添加了完整的API管理页面，路径为 `/api-management`
   - 提供了API列表、创建、编辑和删除功能
   - 支持按名称和路径搜索API
   - 可视化展示API状态（活跃、已弃用、维护中）和权限级别（公开、需要认证、仅管理员）

2. **API测试功能增强**
   - 提供更强大的API测试界面，支持各种HTTP方法
   - 支持请求体的JSON编辑和格式化
   - 支持使用API密钥进行认证测试
   - 可视化展示响应状态、响应时间和响应内容

3. **权限管理**
   - API管理功能仅对管理员开放
   - 可以为每个API端点单独设置权限级别

4. **导航改进**
   - 在左侧导航栏添加了"API管理"子菜单
   - 包含"API测试"和"API接口管理"两个选项

**技术变更：**

1. **前端**
   - 添加了 `ApiManagement.vue` 组件
   - 创建了 `apiManagement.js` API服务
   - 更新了路由配置和导航菜单

2. **后端**
   - 添加了API端点管理相关的API：
     - `POST /api/v1/endpoints/create`
     - `PUT /api/v1/endpoints/{id}/update`
     - `DELETE /api/v1/endpoints/{id}/delete`
   - 实现了相应的视图函数，具备完整的参数验证和错误处理 