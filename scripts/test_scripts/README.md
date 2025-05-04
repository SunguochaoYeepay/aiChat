# 测试脚本说明

本目录包含用于测试Qwen-VL-Chat模型和API服务的各种脚本。

## 脚本说明

### 模型测试

- `test_model_loading.py` - 测试模型加载功能
- `test_model_wrapper.py` - 测试模型包装器类
- `simple_model_test.py` - 简单测试模型功能

### API测试

- `test_chat_api.py` - 测试聊天API接口
- `simple_chat_test.py` - 简单测试聊天功能
- `run_complete_test.py` - 运行完整的功能测试，包括模型加载和API调用

### 系统检查

- `check_gpu.py` - 检查GPU可用性
- `check_model_status.py` - 检查模型服务状态

## 使用方法

所有测试脚本都应该在项目根目录下使用虚拟环境运行：

```
# 从项目根目录运行
cd design-helper
chat_env\Scripts\python.exe scripts\test_scripts\<脚本名称>

# 例如
chat_env\Scripts\python.exe scripts\test_scripts\test_chat_api.py
```

## 注意事项

- 测试脚本需要在模型服务启动前或启动后运行，具体取决于测试目的
- 某些测试脚本会直接加载模型，需要确保GPU有足够内存
- API测试脚本需要确保API服务已经启动 