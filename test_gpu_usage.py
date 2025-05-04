import torch
import json
import requests
import base64
from PIL import Image
import io
import time

def check_gpu_status():
    """检查GPU状态"""
    is_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count() if is_available else 0
    
    gpu_info = {}
    if is_available:
        try:
            for i in range(device_count):
                gpu_info[f"device_{i}"] = {
                    "name": torch.cuda.get_device_name(i),
                    "total_memory_gb": torch.cuda.get_device_properties(i).total_memory / 1024 / 1024 / 1024,
                    "allocated_memory_gb": torch.cuda.memory_allocated(i) / 1024 / 1024 / 1024,
                    "cached_memory_gb": torch.cuda.memory_reserved(i) / 1024 / 1024 / 1024
                }
        except Exception as e:
            gpu_info["error"] = str(e)
    
    return {
        "cuda_available": is_available,
        "device_count": device_count,
        "cuda_version": torch.version.cuda if is_available else "不可用",
        "gpu_info": gpu_info
    }

def create_test_image(color="red", size=(200, 200)):
    """创建测试图像"""
    img = Image.new('RGB', size, color=color)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def test_with_gpu_monitoring():
    """测试API并监控GPU使用情况"""
    # 显示初始GPU状态
    print("初始GPU状态:")
    initial_status = check_gpu_status()
    print(json.dumps(initial_status, indent=2, ensure_ascii=False))
    
    # 创建测试图像
    print("\n创建测试图像...")
    image_base64 = create_test_image("blue")
    
    # 调用API
    url = "http://localhost:8000/api/analyze"
    payload = {
        "image_base64": image_base64,
        "query": "这是什么图片?"
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"\n发送请求到: {url}")
    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    process_time = time.time() - start_time
    
    print(f"响应状态码: {response.status_code}")
    print(f"处理时间: {process_time:.2f}秒")
    
    if response.status_code == 200:
        result = response.json()
        print("分析结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"请求失败: {response.text}")
    
    # 显示API调用后的GPU状态
    print("\nAPI调用后GPU状态:")
    after_status = check_gpu_status()
    print(json.dumps(after_status, indent=2, ensure_ascii=False))
    
    # 比较内存变化
    if initial_status["cuda_available"] and after_status["cuda_available"]:
        for device in after_status["gpu_info"]:
            if device in initial_status["gpu_info"]:
                init_mem = initial_status["gpu_info"][device]["allocated_memory_gb"]
                after_mem = after_status["gpu_info"][device]["allocated_memory_gb"]
                print(f"\n{device} GPU内存变化: {after_mem - init_mem:.2f} GB")

if __name__ == "__main__":
    test_with_gpu_monitoring() 