import requests
import base64
import os
import json
import urllib.request

# 服务器URL
SERVER_URL = "http://localhost:8000"

# 测试图像文件
TEST_IMAGE = "test_image.jpg"

# 如果测试图像不存在，则下载一个测试图像
if not os.path.exists(TEST_IMAGE):
    print(f"下载测试图像...")
    urllib.request.urlretrieve(
        "https://cdn.pixabay.com/photo/2016/11/29/12/17/beach-1869598_1280.jpg", 
        TEST_IMAGE
    )
    print(f"测试图像已下载: {TEST_IMAGE}")
else:
    print(f"测试图像已存在: {TEST_IMAGE}")

# 将图像转换为base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 测试图像分析API
def test_image_analysis():
    # 准备请求数据
    image_base64 = image_to_base64(TEST_IMAGE)
    payload = {
        "image_base64": image_base64,
        "query": "这张图片是什么?"
    }
    
    print("发送图像分析请求...")
    response = requests.post(f"{SERVER_URL}/analyze", json=payload)
    
    if response.status_code == 200:
        print("分析成功:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 检查是否返回了边界框图像URL
        response_data = response.json()
        if "boxed_image_url" in response_data:
            print(f"返回了边界框图像URL: {response_data['boxed_image_url']}")
            if "boxed_image_full_url" in response_data:
                print(f"完整URL: {response_data['boxed_image_full_url']}")
                # 尝试获取边界框图像
                try:
                    img_response = requests.get(response_data['boxed_image_full_url'])
                    print(f"边界框图像访问状态码: {img_response.status_code}")
                except Exception as e:
                    print(f"获取边界框图像失败: {e}")
        else:
            print("响应中没有边界框图像URL")
            
        # 检查是否有边界框错误信息
        if "box_image_error" in response_data:
            print(f"边界框图像错误: {response_data['box_image_error']}")
    else:
        print("分析失败:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

# 测试目标检测API
def test_target_detection():
    # 准备请求数据
    image_base64 = image_to_base64(TEST_IMAGE)
    payload = {
        "image_base64": image_base64,
        "query": "框出图中的狗"
    }
    
    print("\n发送目标检测请求...")
    response = requests.post(f"{SERVER_URL}/analyze", json=payload)
    
    if response.status_code == 200:
        print("检测成功:")
        print(f"状态码: {response.status_code}")
        response_data = response.json()
        print(f"响应: {response_data}")
        
        # 打印所有响应字段
        print(f"响应的所有键: {list(response_data.keys())}")
        print(f"原始响应文本(前200字符): {json.dumps(response_data)[:200]}")
        
        # 检查是否成功检测到边界框
        if "result" in response_data and ("<box>" in response_data["result"]):
            print("成功检测到边界框!")
            print(f"边界框文本: {response_data['result']}")
            
            # 检查是否返回了边界框图像URL
            if "boxed_image_url" in response_data:
                print(f"边界框图像URL: {response_data['boxed_image_url']}")
                if "boxed_image_full_url" in response_data:
                    print(f"完整URL: {response_data['boxed_image_full_url']}")
                    # 尝试获取边界框图像
                    try:
                        img_response = requests.get(response_data['boxed_image_full_url'])
                        print(f"边界框图像访问状态码: {img_response.status_code}")
                    except Exception as e:
                        print(f"获取边界框图像失败: {e}")
            else:
                print("响应中没有找到边界框图像URL")
                
            # 检查是否有边界框错误信息
            if "box_image_error" in response_data:
                print(f"边界框图像错误: {response_data['box_image_error']}")
        else:
            print("未检测到边界框")
    else:
        print("检测失败:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

# 测试多目标检测API
def test_multi_target_detection():
    # 准备请求数据
    image_base64 = image_to_base64(TEST_IMAGE)
    payload = {
        "image_base64": image_base64,
        "query": "找到并标记出图中的人和狗"
    }
    
    print("\n发送多目标检测请求...")
    response = requests.post(f"{SERVER_URL}/analyze", json=payload)
    
    if response.status_code == 200:
        print("检测成功:")
        print(f"状态码: {response.status_code}")
        response_data = response.json()
        print(f"响应: {response_data}")
        
        # 打印所有响应字段
        print(f"响应的所有键: {list(response_data.keys())}")
        
        # 检查是否成功检测到边界框
        if "result" in response_data and ("<box>" in response_data["result"]):
            print("成功检测到边界框!")
            
            # 检查是否返回了边界框图像URL
            if "boxed_image_url" in response_data:
                print(f"边界框图像URL: {response_data['boxed_image_url']}")
                if "boxed_image_full_url" in response_data:
                    print(f"完整URL: {response_data['boxed_image_full_url']}")
                    # 尝试获取边界框图像
                    try:
                        img_response = requests.get(response_data['boxed_image_full_url'])
                        print(f"边界框图像访问状态码: {img_response.status_code}")
                    except Exception as e:
                        print(f"获取边界框图像失败: {e}")
            else:
                print("响应中没有找到边界框图像URL")
                
            # 检查是否有边界框错误信息
            if "box_image_error" in response_data:
                print(f"边界框图像错误: {response_data['box_image_error']}")
        else:
            print("未检测到边界框")
    else:
        print("检测失败:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

if __name__ == "__main__":
    test_image_analysis()
    test_target_detection()
    test_multi_target_detection() 