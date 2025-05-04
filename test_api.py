#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time

# 设置服务器地址
BASE_URL = "http://127.0.0.1:8000"

def test_status_api():
    """测试服务状态接口"""
    try:
        url = f"{BASE_URL}/status"
        response = requests.get(url, timeout=5)
        print(f"状态接口 /status 测试结果：")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"测试状态接口出错: {str(e)}")
        return False

def test_search_api():
    """测试知识库搜索接口"""
    try:
        url = f"{BASE_URL}/search"
        payload = {
            "query": "图像分析",
            "top_k": 3
        }
        response = requests.post(url, json=payload, timeout=5)
        print(f"\n搜索接口 /search 测试结果：")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"测试搜索接口出错: {str(e)}")
        return False

def test_chat_api():
    """测试聊天接口"""
    try:
        url = f"{BASE_URL}/v1/chat/completions"
        payload = {
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你的功能"}
            ],
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=10)
        print(f"\n聊天接口 /v1/chat/completions 测试结果：")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"测试聊天接口出错: {str(e)}")
        return False

def main():
    print("开始测试API接口...\n")
    
    # 测试状态接口
    status_api_ok = test_status_api()
    
    # 测试搜索接口
    search_api_ok = test_search_api()
    
    # 测试聊天接口
    chat_api_ok = test_chat_api()
    
    # 总结测试结果
    print("\n测试结果总结:")
    print(f"状态接口: {'可用 ✓' if status_api_ok else '不可用 ✗'}")
    print(f"搜索接口: {'可用 ✓' if search_api_ok else '不可用 ✗'}")
    print(f"聊天接口: {'可用 ✓' if chat_api_ok else '不可用 ✗'}")
    
    if status_api_ok and search_api_ok and chat_api_ok:
        print("\n所有接口测试通过，系统正常运行！")
    else:
        print("\n部分接口测试失败，请检查系统运行状态。")

if __name__ == "__main__":
    main() 