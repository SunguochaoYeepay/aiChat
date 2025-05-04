"""
单图分析测试模块

此模块用于测试图像分析API处理单个复杂图片的性能和GPU使用情况。
"""
import requests
import json
import time
import sys
import base64
import logging
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                "allocated_memory": gpu_info.get("allocated_memory", 0),
                "cached_memory": gpu_info.get("cached_memory", 0),
                "name": gpu_info.get("name", "unknown")
            }
    except Exception as e:
        logger.exception(f"获取GPU状态时出错: {str(e)}")
    
    return {
        "gpu_available": False,
        "allocated_memory": 0,
        "cached_memory": 0,
        "name": "unknown"
    }

def encode_image(image_path):
    """将图片文件转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"编码图片时出错: {str(e)}")
        return None

def analyze_image(base_url, image_path, query="这是什么图片？请详细描述。"):
    """分析图片内容"""
    url = f"{base_url}/api/analyze"
    
    # 将图片转换为base64
    image_base64 = encode_image(image_path)
    if not image_base64:
        logger.error(f"无法编码图片: {image_path}")
        return None
    
    # 准备请求数据
    data = {
        "image_base64": image_base64,
        "query": query
    }
    
    logger.info(f"开始分析图片: {os.path.basename(image_path)}")
    logger.info(f"查询问题: {query}")
    
    # 获取请求前的GPU状态
    gpu_before = get_gpu_status(base_url)
    logger.info(f"请求前GPU状态: 已分配={gpu_before['allocated_memory']}GB, 缓存={gpu_before['cached_memory']}GB")
    
    # 发送请求并计时
    try:
        start_time = time.time()
        response = requests.post(url, json=data, timeout=120)  # 增加超时时间，复杂图片可能需要更长处理时间
        end_time = time.time()
        
        processing_time = end_time - start_time
        logger.info(f"图片处理耗时: {processing_time:.2f}秒")
        
        # 获取请求后的GPU状态
        gpu_after = get_gpu_status(base_url)
        logger.info(f"请求后GPU状态: 已分配={gpu_after['allocated_memory']}GB, 缓存={gpu_after['cached_memory']}GB")
        
        # 计算内存变化
        memory_change = gpu_after['allocated_memory'] - gpu_before['allocated_memory']
        logger.info(f"GPU内存变化: {memory_change:.2f}GB")
        
        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()
                logger.info(f"分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return {
                    "success": True,
                    "processing_time": processing_time,
                    "result": result,
                    "memory_change": memory_change,
                    "gpu_used": gpu_before["gpu_available"] and (abs(memory_change) > 0.1)
                }
            except json.JSONDecodeError:
                logger.error(f"无法解析JSON响应: {response.text}")
        else:
            logger.error(f"请求失败，状态码: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
        
    except Exception as e:
        logger.exception(f"请求异常: {str(e)}")
    
    return {
        "success": False,
        "processing_time": 0,
        "result": None,
        "memory_change": 0,
        "gpu_used": False
    }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        logger.error("请提供图片路径！用法: python test_single_image.py <图片路径> [API基础URL]")
        return 1
    
    image_path = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        logger.error(f"图片不存在: {image_path}")
        return 1
    
    # 执行分析
    result = analyze_image(base_url, image_path)
    
    # 输出报告
    logger.info("\n测试报告:")
    logger.info(f"测试图片: {image_path}")
    logger.info(f"成功状态: {'成功' if result['success'] else '失败'}")
    logger.info(f"处理时间: {result['processing_time']:.2f}秒")
    logger.info(f"GPU使用: {'是' if result['gpu_used'] else '否'}")
    logger.info(f"GPU内存变化: {result['memory_change']:.2f}GB")
    
    # 输出分析结果
    if result['success'] and result['result']:
        if isinstance(result['result'], dict) and 'result' in result['result']:
            logger.info(f"分析结果: {result['result']['result']}")
        else:
            logger.info(f"分析结果: {result['result']}")
    
    return 0 if result['success'] else 1

if __name__ == "__main__":
    sys.exit(main()) 