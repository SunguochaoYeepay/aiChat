import os
import base64
import json
import requests
from PIL import Image
import io
import time

# 创建测试图像
def create_test_image(color="red", size=(200, 200)):
    img = Image.new('RGB', size, color=color)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# 调用API
def test_image_api(image_base64, query="这是什么图片?"):
    try:
        url = "http://localhost:8000/api/analyze"
        payload = {
            "image_base64": image_base64,
            "query": query
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"发送请求到: {url}")
        print(f"查询问题: {query}")
        
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        end_time = time.time()
        
        print(f"响应状态码: {response.status_code}")
        print(f"处理时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("分析结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求发生错误: {e}")
        return None

if __name__ == "__main__":
    print("创建测试图像...")
    red_image = create_test_image("red")
    
    print("\n测试红色图像:")
    test_image_api(red_image)
    
    # 可以添加更多测试
    colors = ["green", "blue", "yellow", "black"]
    for color in colors:
        print(f"\n\n测试{color}色图像:")
        color_image = create_test_image(color)
        test_image_api(color_image) 