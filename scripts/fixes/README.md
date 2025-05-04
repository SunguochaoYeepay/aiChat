# 修复脚本

此目录包含用于修复和优化系统的脚本。

## 脚本列表

- `fix_api_service.py` - 修复API服务的Python脚本
  - 解决Django启动问题
  - 初始化向量搜索功能
  - 确保sentence-transformers库正确加载
  - 修复"模型未加载"警告
  
- `fix_api_service.bat` - 运行修复脚本的Windows批处理文件

## 使用方法

### 运行修复脚本

直接双击`fix_api_service.bat`或在命令行中运行：

```bash
cd scripts/fixes
python fix_api_service.py
```

### 注意事项

1. 运行修复脚本前，请确保已安装所有必要的依赖：
   ```bash
   pip install sentence-transformers faiss-cpu
   ```

2. 修复脚本会先执行数据库迁移，确保所有表格已创建

3. 如果遇到"模型未加载"警告，请运行此修复脚本 