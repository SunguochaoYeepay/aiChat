import requests
import json
import time
import sys

def test_chat_api(base_url="http://localhost:8000"):
    """
    测试聊天API
    
    Args:
        base_url: API基础URL
    """
    # 组合完整URL
    url = f"{base_url}/api/v1/chat/completions"
    
    # 准备测试消息
    messages = [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "你好，请介绍一下自己。"}
    ]
    
    # 准备请求数据
    data = {
        "messages": messages,
        "stream": False
    }
    
    print(f"\n正在测试聊天API: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        # 发送POST请求
        start_time = time.time()
        response = requests.post(url, json=data)
        end_time = time.time()
        
        # 打印响应时间
        print(f"\n响应时间: {end_time - start_time:.2f}秒")
        
        # 检查响应状态
        if response.status_code == 200:
            # 尝试解析JSON响应
            try:
                result = response.json()
                print(f"\n响应状态码: {response.status_code}")
                
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
            
            except json.JSONDecodeError:
                print(f"无法解析JSON响应: {response.text}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")

if __name__ == "__main__":
    # 从命令行参数获取URL或使用默认值
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_chat_api(base_url) 