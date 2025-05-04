# 脚本目录

此目录包含项目中使用的各种脚本，分为以下几个类别：

## startup/

启动相关脚本，用于启动API服务。

- `startup.py` - 主启动脚本，用于加载模型并启动Django服务
- `load_model_and_run_django.py` - 先加载模型，再启动Django服务的脚本
- `load_model.py` - 仅加载模型的脚本

## fixes/

修复和优化脚本，用于解决各种问题。

- `fix_api_service.py` - 修复API服务，解决"模型未加载"等问题
- `fix_api_service.bat` - Windows批处理文件，用于执行修复脚本

## test_scripts/

测试相关脚本，用于测试各个功能。

- `test_chat_api.py` - 测试聊天API是否正常工作
- `setup_vector_search.py` - 设置和测试向量搜索功能
- `run_test.bat` - 运行测试的批处理文件

## utils/

实用工具脚本，提供各种辅助功能。

## 使用方法

### 启动服务

要启动API服务，请使用根目录下的`start_api_service.bat`，它提供了多种启动选项：

1. 标准启动 - 使用原始启动脚本
2. 修复模式 - 使用修复脚本，优化向量搜索和解决警告
3. 仅测试API

### 测试功能

要测试特定功能：

```bash
# 测试聊天API
python scripts/test_scripts/test_chat_api.py

# 测试向量搜索功能
python scripts/test_scripts/setup_vector_search.py
``` 