import torch

# 检查CUDA是否可用
print(f"CUDA是否可用: {torch.cuda.is_available()}")

# 如果CUDA可用，打印GPU信息
if torch.cuda.is_available():
    print(f"GPU数量: {torch.cuda.device_count()}")
    print(f"当前GPU: {torch.cuda.current_device()}")
    print(f"GPU名称: {torch.cuda.get_device_name(0)}")
    
    # 打印CUDA版本
    print(f"CUDA版本: {torch.version.cuda}")

# 打印PyTorch信息
print(f"PyTorch版本: {torch.__version__}") 