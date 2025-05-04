import os
import sys
import time
import json
import requests
from pathlib import Path

# 将项目目录添加到Python路径
current_dir = Path.cwd()
admin_system_dir = current_dir / "admin_system"
sys.path.append(str(admin_system_dir))

# 设置Django环境使用最小化设置（不启动Django服务器）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings')

try:
    print("初始化Django...")
    import django
    django.setup()
    print("Django初始化完成")
    
    # 预加载模型
    print("\n预加载模型...")
    from core.model_service import init_model, get_service_status, get_model
    
    # 直接指定模型路径进行初始化
    model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
    device = "cuda"
    precision = "float16"
    
    print(f"使用以下配置加载模型:")
    print(f"路径: {model_path}")
    print(f"设备: {device}")
    print(f"精度: {precision}")
    
    # 初始化并加载模型
    result = init_model(model_path, device, precision)
    print(f"模型加载结果: {result}")
    
    # 获取并打印服务状态
    status = get_service_status()
    print("\n模型服务状态:")
    print(f"状态: {status.get('status', 'unknown')}")
    print(f"消息: {status.get('message', 'unknown')}")
    print(f"模型已加载: {status.get('model_loaded', False)}")
    print(f"GPU可用: {status.get('gpu_available', False)}")
    
    # 直接使用模型进行测试
    print("\n直接使用模型进行测试...")
    model, tokenizer = get_model()
    
    if model is None or tokenizer is None:
        print("错误: 模型或分词器未加载")
    else:
        # 测试消息
        test_prompt = "你好，请介绍一下自己"
        history = []
        
        # 使用模型进行对话
        print(f"提问: {test_prompt}")
        start_time = time.time()
        response, new_history = model.chat(tokenizer, test_prompt, history=history)
        end_time = time.time()
        
        print(f"响应时间: {end_time - start_time:.2f}秒")
        print(f"回答: {response}")
    
    # 使用文本处理模块测试聊天功能
    print("\n使用文本处理模块测试聊天功能...")
    from core.text_processing import chat_completion
    
    # 准备测试消息
    test_messages = [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "你好，请用一句话介绍一下自己。"}
    ]
    
    # 调用聊天功能
    start_time = time.time()
    result = chat_completion(test_messages)
    end_time = time.time()
    
    # 打印结果
    print(f"处理时间: {end_time - start_time:.2f}秒")
    print("\n聊天结果:")
    if isinstance(result, dict):
        if "error" in result:
            print(f"错误: {result['error']}")
        elif "choices" in result and result["choices"]:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                print(f"回复: {choice['message']['content']}")
            else:
                print(f"未找到回复内容: {choice}")
        else:
            print(f"未知结果格式: {result}")
    else:
        print(f"未知结果类型: {type(result)}")
    
except Exception as e:
    print(f"测试过程中出错: {str(e)}")
    import traceback
    traceback.print_exc() 