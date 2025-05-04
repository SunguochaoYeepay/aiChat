import os
import sys
import traceback
import torch

try:
    print("开始测试模型加载...")
    
    # 模型路径
    model_path = 'D:/AI-DEV/models/Qwen-VL-Chat-Int4'
    
    # 检查模型路径是否存在
    if os.path.exists(model_path):
        print(f"模型路径存在: {model_path}")
    else:
        print(f"模型路径不存在: {model_path}")
        sys.exit(1)
    
    # 检查GPU可用性
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    if device == 'cuda':
        print(f"GPU名称: {torch.cuda.get_device_name(0)}")
        print(f"GPU可用内存: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB")
    
    # 导入必要的库
    print("导入transformers库...")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # 加载tokenizer
    print(f"正在加载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    print("tokenizer加载成功")
    
    # 加载模型
    print(f"正在加载模型...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
        use_cache=True
    )
    print("模型加载成功")
    
    # 将模型移至指定设备
    if device == 'cuda':
        print("将模型移至GPU...")
        model = model.to(device)
    
    # 将模型设置为评估模式
    model = model.eval()
    
    # 测试基本对话
    print("\n测试基本对话功能...")
    
    # 检查model.chat方法是否存在
    if hasattr(model, 'chat'):
        print("模型具有chat方法")
        
        # 测试对话
        response, history = model.chat(tokenizer, "你好，请介绍一下自己", history=[])
        print(f"模型响应: {response}")
    else:
        print("警告: 模型没有chat方法")
        print(f"模型类型: {type(model)}")
        print(f"可用方法: {dir(model)}")
    
    print("模型测试完成")
    
except Exception as e:
    print(f"出错了: {str(e)}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
print("脚本执行完毕") 