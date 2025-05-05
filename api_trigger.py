import requests
import json
import time
import sys

def trigger_model_load(port=8001):
    """发送请求触发模型加载并检查状态"""
    base_url = f"http://127.0.0.1:{port}"
    print("正在发送初始请求以触发模型完全加载...")
    
    # 发送初始化请求
    try:
        response = requests.post(
            f"{base_url}/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "hello"}]},
            timeout=30
        )
        print(f"请求已发送。状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.text}")
            return False
            
        # 等待几秒让模型初始化
        print("等待模型完全初始化...")
        time.sleep(5)
        
        # 检查状态
        status_response = requests.get(f"{base_url}/api/status")
        status = status_response.json()
        status_str = json.dumps(status, ensure_ascii=False, indent=2)
        print(f"服务状态: {status_str}")
        
        if status.get("model_loaded"):
            print("模型已成功加载！")
            return True
        else:
            print("模型似乎未完全加载，请检查日志。")
            return False
            
    except Exception as e:
        print(f"发送请求时出错: {str(e)}")
        return False

if __name__ == "__main__":
    port = 8001
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    trigger_model_load(port) 