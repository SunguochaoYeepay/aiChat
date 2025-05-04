# 启动脚本说明

本目录包含用于启动和运行Qwen-VL-Chat API服务的脚本。

## 脚本说明

### 核心脚本

- `startup.py` - 主要启动脚本，负责初始化Django、加载模型并启动API服务
- `load_model_and_run_django.py` - 加载模型并启动Django的脚本
- `load_model.py` - 仅加载模型的独立脚本
- `start_service.bat` - 批处理启动脚本

## 使用方法

### 从本目录启动

可以直接双击本目录中的`start_service.bat`启动服务：

```
# 双击启动
scripts\startup\start_service.bat
```

此批处理文件会自动切换到项目根目录，激活虚拟环境并运行启动脚本。

### 从项目根目录启动

也可以使用项目根目录中的批处理文件启动：

```
# 双击启动
start_service.bat
```

## 配置说明

主要配置参数在`startup.py`文件中：

- `model_path` - 模型路径，默认为`D:/AI-DEV/models/Qwen-VL-Chat-Int4`
- `device` - 设备类型，默认为`cuda`
- `precision` - 精度，默认为`float16`

如需修改，请直接编辑`startup.py`文件中的相应变量。

## 注意事项

- 启动服务前请确保模型文件已正确下载并放置在指定位置
- 启动服务需要足够的GPU内存
- 启动过程会占用较多系统资源，请耐心等待
- 服务默认在`8000`端口启动，请确保该端口未被占用 