# 测试脚本说明

本目录包含用于测试后端API和模型服务的各种测试脚本。这些脚本用于验证系统的各个组件是否正常工作，特别是在代码更改或环境变更后。

## 主要测试脚本

- `test_single_image.py` - 测试单图像分析API
- `test_multi_images_analyze.py` - 测试多图像并发分析API
- `test_image_direct.py` - 测试不同格式的图像输入
- `test_image_fixed.py` - 测试修复后的图像分析功能
- `test_chat_api.py` - 测试聊天API
- `test_search_api.py` - 测试搜索API
- `test_model_status.py` - 测试模型状态API
- `test_model_loading.py` - 测试模型加载功能
- `test_model_wrapper.py` - 测试模型包装器

## 实用工具

- `check_gpu.py` - 检查GPU可用性和状态
- `run_all_tests.bat` - 批处理脚本，运行所有测试
- `run_test.bat` - 批处理脚本，运行单个测试

## 图像分析测试详情

最近修复了图像分析API中的参数传递问题。`test_image_api.py`和`test_gpu_usage.py`是专门为验证这一修复而创建的脚本：

- `test_image_api.py` - 测试不同颜色图像的分析结果
- `test_gpu_usage.py` - 测试图像分析过程中的GPU使用情况

修复前问题：
- 模型调用参数错误：`model.chat(tokenizer, query=query, image=image, history=[])`
- 导致错误提示：`The following model_kwargs are not used by the model: ['image']`
- GPU未被使用，导致处理时间延长

修复后结果：
- 正确使用`tokenizer.from_list_format()`构建输入
- 成功使用GPU处理图像，提高了处理速度
- 正确处理RGBA图像格式问题

## 运行测试

在项目根目录运行：

```bash
python scripts/test_scripts/test_image_api.py
python scripts/test_scripts/test_gpu_usage.py
```

或使用批处理脚本：

```bash
scripts/test_scripts/run_test.bat test_image_api.py
```

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