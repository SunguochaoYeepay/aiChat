# Qwen-VL-Chat 启动说明

## 文件结构

项目文件已重新组织为以下结构：

```
design-helper/
├── start.bat              # 【主入口】中文版启动脚本
├── start_en.bat           # 【主入口】英文版启动脚本
├── docs/                  # 文档目录
│   ├── 启动说明.md         # 详细启动说明
│   └── readme/            # 其他语言说明文档
├── scripts/               # 脚本目录
│   ├── launchers/         # 所有启动脚本
│   ├── patches/           # 补丁文件
│   ├── startup/           # 核心启动脚本
│   └── tests/             # 测试脚本
└── 其他文件和目录...
```

## 快速开始

1. 双击运行根目录下的 `start.bat`（中文）或 `start_en.bat`（英文）
2. 在启动器界面中选择合适的启动方式
3. 推荐选择 `start_all_services.bat` 或 `start_simple.bat` 并使用**完整启动**选项

## 启动器选项说明

- `start_all_services.bat` - 中文界面，一键启动（推荐）
- `start_simple.bat` - 英文界面，一键启动（推荐）
- `fix_and_start.bat` - 修复模式，解决模型加载问题
- `start_and_load.bat` - 后台启动服务
- `start_api_service.bat` - 多选项API启动
- `start_service.bat` - 简单启动（不推荐）

详细说明请参阅 `docs/启动说明.md` 文件。 