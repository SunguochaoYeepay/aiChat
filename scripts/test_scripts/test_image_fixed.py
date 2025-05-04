"""
修复版单图分析测试模块

此模块用于测试图像分析API处理单个复杂图片的性能和GPU使用情况，
并尝试修复image参数问题。
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

def analyze_image_with_format(base_url, image_path, query="请详细描述这张图片的内容", format_type=1):
    """测试不同格式的图片分析请求"""
    url = f"{base_url}/api/analyze"
    
    # 将图片转换为base64
    image_base64 = encode_image(image_path)
    if not image_base64:
        logger.error(f"无法编码图片: {image_path}")
        return None
    
    # 根据format_type使用不同的请求格式
    if format_type == 1:
        # 原始格式
        data = {
            "image_base64": image_base64,
            "query": query
        }
        logger.info("使用原始请求格式: image_base64参数")
    elif format_type == 2:
        # 尝试直接使用image参数
        data = {
            "image": image_base64,
            "query": query
        }
        logger.info("使用尝试格式2: image参数")
    elif format_type == 3:
        # 尝试将图像包含在消息格式中
        data = {
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]}
            ]
        }
        logger.info("使用尝试格式3: OpenAI风格的消息格式")
    elif format_type == 4:
        # 尝试将图像和查询包装在content字段中
        data = {
            "content": {
                "image_base64": image_base64,
                "query": query
            }
        }
        logger.info("使用尝试格式4: content包装")
    else:
        # 默认使用原始格式
        data = {
            "image_base64": image_base64,
            "query": query
        }
        logger.info("使用默认请求格式")
    
    logger.info(f"开始分析图片: {os.path.basename(image_path)}")
    logger.info(f"查询问题: {query}")
    
    # 获取请求前的GPU状态
    gpu_before = get_gpu_status(base_url)
    logger.info(f"请求前GPU状态: 已分配={gpu_before['allocated_memory']}GB, 缓存={gpu_before['cached_memory']}GB")
    
    # 发送请求并计时
    try:
        start_time = time.time()
        response = requests.post(url, json=data, timeout=120)
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
                    "gpu_used": gpu_before["gpu_available"] and (abs(memory_change) > 0.1),
                    "format_type": format_type
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
        "gpu_used": False,
        "format_type": format_type
    }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        logger.error("请提供图片路径！用法: python test_image_fixed.py <图片路径> [API基础URL]")
        return 1
    
    image_path = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        logger.error(f"图片不存在: {image_path}")
        return 1
    
    # 尝试所有格式
    results = []
    for format_type in range(1, 5):
        logger.info(f"\n=== 尝试格式 {format_type} ===")
        result = analyze_image_with_format(base_url, image_path, format_type=format_type)
        results.append(result)
        
        # 如果找到成功的格式，则可以提前退出
        if result and result.get("success") and "error" not in result.get("result", {}):
            logger.info(f"找到有效的请求格式: {format_type}")
            break
    
    # 找出最佳结果
    best_result = None
    for result in results:
        if result and result.get("success"):
            # 如果之前没有最佳结果，或者当前结果没有错误而之前的有
            if not best_result or ("error" not in result.get("result", {}) and "error" in best_result.get("result", {})):
                best_result = result
    
    if not best_result:
        logger.error("所有请求格式都失败了")
        return 1
    
    # 输出最佳结果的报告
    logger.info("\n=== 最佳测试报告 ===")
    logger.info(f"测试图片: {image_path}")
    logger.info(f"成功状态: {'成功' if best_result['success'] else '失败'}")
    logger.info(f"最佳请求格式: {best_result['format_type']}")
    logger.info(f"处理时间: {best_result['processing_time']:.2f}秒")
    logger.info(f"GPU使用: {'是' if best_result['gpu_used'] else '否'}")
    logger.info(f"GPU内存变化: {best_result['memory_change']:.2f}GB")
    
    # 输出分析结果
    if best_result['success'] and best_result['result']:
        if isinstance(best_result['result'], dict) and 'result' in best_result['result']:
            logger.info(f"分析结果: {best_result['result']['result']}")
        else:
            logger.info(f"分析结果: {best_result['result']}")
    
    return 0 if best_result['success'] else 1

if __name__ == "__main__":
    sys.exit(main()) 