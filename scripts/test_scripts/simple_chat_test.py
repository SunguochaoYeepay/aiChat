import os
import sys
import time
from pathlib import Path

# 将admin_system添加到Python路径
current_dir = Path.cwd()
admin_system_dir = current_dir / "admin_system"
sys.path.append(str(admin_system_dir))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')

try:
    print("初始化Django...")
    import django
    django.setup()
    print("Django初始化完成")
    
    # 导入核心模块
    from core.text_processing import chat_completion
    
    # 准备测试消息
    test_messages = [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
    
    # 调用聊天功能
    print("\n测试聊天功能...")
    start_time = time.time()
    result = chat_completion(test_messages)
    end_time = time.time()
    
    # 打印结果
    print(f"\n处理时间: {end_time - start_time:.2f}秒")
    print("\n结果:")
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