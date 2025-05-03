import requests
import json
import time

# 测试/status接口
try:
    print("测试GPU服务状态...")
    status_url = "http://localhost:8000/status"
    response = requests.get(status_url, timeout=5)
    if response.status_code == 200:
        print("服务状态响应:")
        data = response.json()
        print(f"  模型ID: {data.get('model_id')}")
        print(f"  设备: {data.get('device')}")
        print(f"  GPU信息: {json.dumps(data.get('gpu_info'), ensure_ascii=False, indent=2)}")
        print(f"  知识库主题: {data.get('kb_topics')}")
    else:
        print(f"错误: {response.status_code} - {response.text}")
except Exception as e:
    print(f"连接服务失败: {e}")

# 测试聊天接口
try:
    print("\n测试聊天接口...")
    chat_url = "http://localhost:8000/v1/chat/completions"
    chat_data = {
        "messages": [
            {"role": "user", "content": "你好，介绍一下你自己"}
        ]
    }
    
    start_time = time.time()
    response = requests.post(chat_url, json=chat_data)
    total_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"总请求时间: {total_time:.2f}秒")
        print(f"服务器处理时间: {data.get('processing_time')}")
        print(f"回复内容: {data['choices'][0]['message']['content'][:100]}...")
    else:
        print(f"错误: {response.status_code} - {response.text}")
except Exception as e:
    print(f"调用聊天接口失败: {e}")

print("\n如果GPU配置正确，处理时间应该明显快于CPU。")
print("请访问测试页面进行更多测试: http://localhost:8000/static/test.html") 