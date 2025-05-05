"""
模型加载触发脚本 - 简化版
此脚本用于向API发送简单请求以触发模型加载
"""
import requests
import json
import time
import sys
import os

def trigger_model_load(port=8001, timeout=60):
    """
    发送请求触发模型加载并检查状态
    
    Args:
        port: API服务端口
        timeout: 等待模型加载的最大时间(秒)
    
    Returns:
        bool: 是否成功加载模型
    """
    base_url = f"http://127.0.0.1:{port}"
    print(f"正在使用API触发脚本 (端口: {port})")
    print("正在发送初始请求以触发模型完全加载...")
    
    # 检查服务是否可用
    try:
        status_resp = requests.get(f"{base_url}/api/status", timeout=5)
        if status_resp.status_code != 200:
            print(f"API服务不可用，状态码: {status_resp.status_code}")
            return False
    except Exception as e:
        print(f"无法连接到API服务: {str(e)}")
        return False
    
    # 检查初始状态
    try:
        status = status_resp.json()
        print(f"当前服务状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
        
        if status.get("model_loaded", False):
            print("模型已加载，无需触发")
            return True
    except Exception as e:
        print(f"解析状态响应时出错: {str(e)}")
    
    # 发送初始化请求
    try:
        response = requests.post(
            f"{base_url}/api/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "你好"}], "max_tokens": 10},
            timeout=30
        )
        print(f"请求已发送。状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.text}")
            return False
            
        # 等待并检查模型加载状态
        print(f"等待模型完全初始化(最多 {timeout} 秒)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status_response = requests.get(f"{base_url}/api/status", timeout=5)
                status = status_response.json()
                
                # 定期输出状态
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 or elapsed < 5:  # 前5秒每秒输出，之后每10秒输出
                    status_str = json.dumps(status, ensure_ascii=False, indent=2)
                    print(f"[{elapsed}秒] 服务状态: {status.get('status', '未知')}")
                
                if status.get("model_loaded"):
                    print("模型已成功加载！")
                    return True
            except Exception as e:
                print(f"检查状态时出错: {str(e)}")
            
            time.sleep(1)
        
        print(f"等待超时 ({timeout}秒)，模型未完全加载")
        print("提示: 可以使用增强版的model_loader.py脚本，或延长等待时间")
        return False
            
    except Exception as e:
        print(f"发送请求时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("API触发脚本开始执行")
    print("=" * 50)
    
    # 获取参数
    port = 8001
    timeout = 60
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"无效的端口参数: {sys.argv[1]}，使用默认端口8001")
    
    if len(sys.argv) > 2:
        try:
            timeout = int(sys.argv[2])
        except ValueError:
            print(f"无效的超时参数: {sys.argv[2]}，使用默认超时60秒")
    
    # 提示使用model_loader.py
    print("注意: 此脚本是简化版触发器，推荐使用model_loader.py获得更好效果")
    print(f"参数: 端口={port}, 超时={timeout}秒")
    
    # 执行模型加载触发
    success = trigger_model_load(port, timeout)
    
    if success:
        print("=" * 50)
        print("模型触发成功!")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print("模型触发未完成，但API服务可能仍在运行")
        print("建议使用增强版model_loader.py脚本完成加载")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main() 