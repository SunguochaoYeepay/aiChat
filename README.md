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