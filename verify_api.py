import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def verify_status_api():
    try:
        print(f"正在测试状态接口: {BASE_URL}/status")
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            print("✓ 状态接口测试通过\n")
            return True
        else:
            print(f"✗ 接口请求失败，状态码: {response.status_code}\n")
            return False
    except Exception as e:
        print(f"✗ 接口请求出错: {str(e)}\n")
        return False

def verify_search_api():
    try:
        print(f"正在测试搜索接口: {BASE_URL}/search")
        payload = {
            "query": "图像分析",
            "top_k": 3
        }
        response = requests.post(f"{BASE_URL}/search", json=payload, timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            print("✓ 搜索接口测试通过\n")
            return True
        else:
            print(f"✗ 接口请求失败，状态码: {response.status_code}\n")
            return False
    except Exception as e:
        print(f"✗ 接口请求出错: {str(e)}\n")
        return False

def verify_chat_api():
    try:
        print(f"正在测试聊天接口: {BASE_URL}/v1/chat/completions")
        payload = {
            "messages": [
                {"role": "user", "content": "你好，请简单介绍一下你的功能"}
            ],
            "stream": False
        }
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            print("✓ 聊天接口测试通过\n")
            return True
        else:
            print(f"✗ 接口请求失败，状态码: {response.status_code}\n")
            return False
    except Exception as e:
        print(f"✗ 接口请求出错: {str(e)}\n")
        return False

if __name__ == "__main__":
    print("=== API接口验证开始 ===\n")
    
    status_ok = verify_status_api()
    search_ok = verify_search_api()
    chat_ok = verify_chat_api()
    
    print("=== API接口验证结果 ===")
    print(f"状态接口: {'✓ 通过' if status_ok else '✗ 失败'}")
    print(f"搜索接口: {'✓ 通过' if search_ok else '✗ 失败'}")
    print(f"聊天接口: {'✓ 通过' if chat_ok else '✗ 失败'}")
    
    if status_ok and search_ok and chat_ok:
        print("\n✅ 所有接口测试通过，系统运行正常！")
    else:
        print("\n❌ 部分接口测试失败，请检查错误信息。") 