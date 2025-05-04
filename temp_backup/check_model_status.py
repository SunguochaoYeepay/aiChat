import requests

# 服务状态接口URL
url = "http://127.0.0.1:8000/status"

# 发送GET请求
response = requests.get(url)

# 打印响应状态码
print(f"状态码: {response.status_code}")

# 打印响应内容
try:
    result = response.json()
    print("模型服务状态:")
    print(f"状态: {result.get('status', 'unknown')}")
    print(f"消息: {result.get('message', 'unknown')}")
    print(f"模型已加载: {result.get('model_loaded', False)}")
    print(f"GPU可用: {result.get('gpu_available', False)}")
    
    # 打印GPU信息（如果有）
    gpu_info = result.get('gpu_info', {})
    if gpu_info:
        print("\nGPU信息:")
        print(f"名称: {gpu_info.get('name', 'unknown')}")
        print(f"总内存: {gpu_info.get('total_memory', 0):.2f} GB")
        print(f"已分配内存: {gpu_info.get('allocated_memory', 0):.2f} GB")
        print(f"缓存内存: {gpu_info.get('cached_memory', 0):.2f} GB")
    
    # 打印模型配置（如果有）
    model_config = result.get('model_config', {})
    if model_config:
        print("\n模型配置:")
        print(f"路径: {model_config.get('path', 'unknown')}")
        print(f"设备: {model_config.get('device', 'unknown')}")
        print(f"精度: {model_config.get('precision', 'unknown')}")
        
except Exception as e:
    print(f"解析响应时出错: {str(e)}")
    print("原始响应内容:")
    print(response.text) 