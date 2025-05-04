import os
import sys
import torch
from pathlib import Path

# 设置路径
current_dir = Path.cwd()
admin_system_dir = current_dir / "admin_system"
sys.path.append(str(admin_system_dir))

# 导入模型包装器
try:
    print("正在导入模型包装器...")
    from core.wrappers.model_wrapper import ModelWrapper
    
    # 创建模型包装器实例
    model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"  # 确保这是正确的路径
    print(f"模型路径: {model_path}")
    print(f"CUDA是否可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA设备数量: {torch.cuda.device_count()}")
        print(f"当前CUDA设备: {torch.cuda.current_device()}")
        print(f"CUDA设备名称: {torch.cuda.get_device_name()}")
    
    # 初始化模型包装器
    wrapper = ModelWrapper(model_path)
    
    # 加载模型
    print("\n开始加载模型...")
    load_success = wrapper.load()
    
    if load_success:
        print("\n模型加载成功，测试简单对话")
        prompt = "你好，请介绍一下自己"
        response, _ = wrapper.chat(prompt)
        print(f"\n提问: {prompt}")
        print(f"回答: {response}")
    else:
        print("\n模型加载失败")
    
except Exception as e:
    print(f"测试过程中出错: {str(e)}")
    import traceback
    traceback.print_exc() 