"""
多图像分析API性能测试模块

此模块用于测试图像分析API处理多张图片的性能，并检查GPU使用情况。
"""
import requests
import json
import time
import sys
import base64
import logging
from concurrent import futures
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试图像的base64编码（创建不同颜色的测试图像）
TEST_IMAGES = {
    "红色像素": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    "绿色像素": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "蓝色像素": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPj/HwADBwIAMCbHYQAAAABJRU5ErkJggg==",
    "黄色像素": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z/C/HgAGgwJ/lK3Q6wAAAABJRU5ErkJggg==",
    "黑色像素": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYGD4DwABBAEAfnvhwQAAAABJRU5ErkJggg=="
}

def get_gpu_status(base_url="http://localhost:8000"):
    """获取GPU状态信息"""
    try:
        status_url = f"{base_url}/api/status"
        response = requests.get(status_url)
        if response.status_code == 200:
            status_data = response.json()
            gpu_info = status_data.get("gpu_info", {})
            return {
                "gpu_available": status_data.get("gpu_available", False),
                "allocated_memory_before": gpu_info.get("allocated_memory", 0),
                "cached_memory_before": gpu_info.get("cached_memory", 0)
            }
    except Exception as e:
        logger.exception(f"获取GPU状态时出错: {str(e)}")
    
    return {
        "gpu_available": False,
        "allocated_memory_before": 0,
        "cached_memory_before": 0
    }

def analyze_image(base_url, image_base64, image_name, query="这是什么图片?"):
    """分析单张图片"""
    url = f"{base_url}/api/analyze"
    data = {
        "image_base64": image_base64,
        "query": query
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data, timeout=60)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        result = {
            "image_name": image_name,
            "status_code": response.status_code,
            "processing_time": processing_time
        }
        
        if response.status_code == 200:
            try:
                result["response"] = response.json()
            except json.JSONDecodeError:
                result["error"] = "无法解析JSON响应"
        else:
            result["error"] = response.text
            
        return result
    
    except Exception as e:
        return {
            "image_name": image_name,
            "error": str(e),
            "status_code": 0,
            "processing_time": 0
        }

def test_multi_images(base_url="http://localhost:8000", concurrent=False):
    """
    测试多张图片的分析性能
    
    Args:
        base_url: API基础URL
        concurrent: 是否并发请求
    """
    logger.info(f"{'并发' if concurrent else '顺序'}测试多张图片分析API: {base_url}/api/analyze")
    
    # 获取测试前的GPU状态
    gpu_before = get_gpu_status(base_url)
    logger.info(f"测试前GPU状态: 可用={gpu_before['gpu_available']}, 已分配内存={gpu_before['allocated_memory_before']}GB, 缓存内存={gpu_before['cached_memory_before']}GB")
    
    results = []
    total_start_time = time.time()
    
    if concurrent:
        # 并发请求
        with futures.ThreadPoolExecutor(max_workers=len(TEST_IMAGES)) as executor:
            future_to_image = {
                executor.submit(analyze_image, base_url, image_data, image_name): image_name
                for image_name, image_data in TEST_IMAGES.items()
            }
            
            for future in futures.as_completed(future_to_image):
                image_name = future_to_image[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"图片 '{image_name}' 分析完成，耗时: {result['processing_time']:.2f}秒")
                except Exception as e:
                    logger.error(f"处理图片 '{image_name}' 时出错: {str(e)}")
    else:
        # 顺序请求
        for image_name, image_data in TEST_IMAGES.items():
            logger.info(f"开始分析图片 '{image_name}'...")
            result = analyze_image(base_url, image_data, image_name)
            results.append(result)
            logger.info(f"图片 '{image_name}' 分析完成，耗时: {result['processing_time']:.2f}秒")
    
    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    
    # 获取测试后的GPU状态
    gpu_after = get_gpu_status(base_url)
    logger.info(f"测试后GPU状态: 可用={gpu_after['gpu_available']}, 已分配内存={gpu_after.get('allocated_memory_before', 0)}GB, 缓存内存={gpu_after.get('cached_memory_before', 0)}GB")
    
    # 计算内存变化
    memory_change = gpu_after.get('allocated_memory_before', 0) - gpu_before['allocated_memory_before']
    
    # 汇总结果
    summary = {
        "total_images": len(TEST_IMAGES),
        "successful_requests": sum(1 for r in results if r["status_code"] == 200),
        "failed_requests": sum(1 for r in results if r["status_code"] != 200),
        "total_time": total_time,
        "average_time": sum(r["processing_time"] for r in results) / len(results) if results else 0,
        "gpu_used": gpu_before["gpu_available"],
        "memory_change": memory_change
    }
    
    logger.info("\n测试结果摘要:")
    logger.info(f"总图片数: {summary['total_images']}")
    logger.info(f"成功请求数: {summary['successful_requests']}")
    logger.info(f"失败请求数: {summary['failed_requests']}")
    logger.info(f"总耗时: {summary['total_time']:.2f}秒")
    logger.info(f"平均每张图片处理时间: {summary['average_time']:.2f}秒")
    logger.info(f"GPU使用: {'是' if summary['gpu_used'] else '否'}")
    logger.info(f"GPU内存变化: {summary['memory_change']:.2f}GB")
    
    # 记录每张图片的处理结果
    for result in results:
        if "error" in result:
            logger.warning(f"图片 '{result['image_name']}' 处理出错: {result.get('error', 'unknown error')}")
        elif "response" in result:
            logger.info(f"图片 '{result['image_name']}' 分析结果: {result['response'].get('result', 'unknown')}")
    
    # 判断是否使用了GPU
    if summary["gpu_used"] and abs(memory_change) > 0.1:
        logger.info("测试表明图像分析API使用了GPU")
        return True
    else:
        logger.info("测试表明图像分析API可能未使用GPU")
        return False

if __name__ == "__main__":
    # 从命令行参数获取URL或使用默认值
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # 默认使用并发模式
    concurrent_mode = True if len(sys.argv) <= 2 else (sys.argv[2].lower() == 'true')
    
    # 运行测试
    success = test_multi_images(base_url, concurrent_mode)
    
    # 设置退出码
    sys.exit(0 if success else 1) 