"""
直接调用图像分析功能的测试模块

此模块尝试直接模拟核心图像分析调用，绕过API。
"""
import requests
import json
import time
import sys
import base64
import logging
import os
from PIL import Image
from io import BytesIO

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

def analyze_image_direct(image_path, query="这是什么图片?请详细描述。"):
    """
    模拟admin_system/core/image_analysis.py中的analyze_image函数直接处理图片
    
    Args:
        image_path: 图片路径
        query: 查询问题
    """
    # 创建API请求格式
    url = "http://localhost:8000/api/analyze"
    
    # 将图片转换为base64
    image_base64 = encode_image(image_path)
    if not image_base64:
        logger.error(f"无法编码图片: {image_path}")
        return None
    
    logger.info(f"开始分析图片: {os.path.basename(image_path)}")
    logger.info(f"查询问题: {query}")
    
    # 获取请求前的GPU状态
    gpu_before = get_gpu_status()
    logger.info(f"请求前GPU状态: 已分配={gpu_before['allocated_memory']}GB, 缓存={gpu_before['cached_memory']}GB")
    
    # 准备不同格式的请求数据
    formats = [
        {
            "name": "标准格式: image_base64",
            "data": {
                "image_base64": image_base64,
                "query": query
            }
        },
        {
            "name": "替代格式: image",
            "data": {
                "image": image_base64,
                "query": query
            }
        },
        {
            "name": "替代格式: base64_image",
            "data": {
                "base64_image": image_base64,
                "query": query
            }
        },
        {
            "name": "OpenAI格式: messages",
            "data": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                        ]
                    }
                ]
            }
        }
    ]
    
    # 结果字典
    results = []
    
    # 测试所有格式
    for i, format_data in enumerate(formats):
        format_name = format_data["name"]
        data = format_data["data"]
        
        logger.info(f"\n测试 {format_name}")
        
        try:
            start_time = time.time()
            response = requests.post(url, json=data, timeout=120)
            end_time = time.time()
            
            processing_time = end_time - start_time
            logger.info(f"{format_name} - 处理耗时: {processing_time:.2f}秒")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"{format_name} - 分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    results.append({
                        "format_name": format_name,
                        "format_index": i,
                        "success": True,
                        "processing_time": processing_time,
                        "result": result
                    })
                except json.JSONDecodeError:
                    logger.error(f"{format_name} - 响应不是有效的JSON: {response.text}")
                    results.append({
                        "format_name": format_name,
                        "format_index": i,
                        "success": False,
                        "error": "响应不是有效的JSON"
                    })
            else:
                logger.error(f"{format_name} - 请求失败，状态码: {response.status_code}")
                logger.error(f"{format_name} - 响应内容: {response.text}")
                results.append({
                    "format_name": format_name,
                    "format_index": i,
                    "success": False,
                    "error": response.text
                })
        except Exception as e:
            logger.exception(f"{format_name} - 请求异常: {str(e)}")
            results.append({
                "format_name": format_name,
                "format_index": i,
                "success": False,
                "error": str(e)
            })
    
    # 获取请求后的GPU状态
    gpu_after = get_gpu_status()
    logger.info(f"请求后GPU状态: 已分配={gpu_after['allocated_memory']}GB, 缓存={gpu_after['cached_memory']}GB")
    
    # 计算内存变化
    memory_change = gpu_after['allocated_memory'] - gpu_before['allocated_memory']
    logger.info(f"GPU内存变化: {memory_change:.2f}GB")
    
    # 判断是否使用了GPU
    gpu_used = gpu_before["gpu_available"] and (abs(memory_change) > 0.1)
    logger.info(f"GPU使用: {'是' if gpu_used else '否'}")
    
    # 找出最佳结果
    best_result = None
    for result in results:
        if result['success']:
            if not best_result:
                best_result = result
            elif ('error' not in result.get('result', {}) and 
                  best_result and 'error' in best_result.get('result', {})):
                best_result = result
    
    # 综合测试报告
    logger.info("\n图像分析测试报告:")
    logger.info(f"测试图片: {image_path}")
    if best_result:
        logger.info(f"最佳请求格式: {best_result['format_name']}")
        if best_result['result'].get('result') and 'error' not in best_result['result']:
            text_result = best_result['result'].get('result', '')
            logger.info(f"分析结果: {text_result[:200]}..." if len(text_result) > 200 else text_result)
        else:
            logger.info(f"分析结果包含错误: {best_result['result'].get('error', 'unknown error')}")
    else:
        logger.info("没有成功的请求格式")
    
    logger.info(f"GPU使用: {'是' if gpu_used else '否'}")
    logger.info(f"GPU内存变化: {memory_change:.2f}GB")
    
    # 更详细的结果摘要
    logger.info("\n各格式结果摘要:")
    for result in results:
        status = "成功" if result['success'] else "失败"
        format_name = result['format_name']
        if result['success']:
            if 'error' in result.get('result', {}):
                error_msg = result['result'].get('error', '')
                logger.info(f"{format_name}: {status} (包含错误: {error_msg[:50]}...)" if len(error_msg) > 50 else error_msg)
            else:
                logger.info(f"{format_name}: {status}")
        else:
            error_msg = result.get('error', 'unknown error')
            logger.info(f"{format_name}: {status} (错误: {error_msg[:50]}...)" if len(error_msg) > 50 else error_msg)
    
    return {
        "success": bool(best_result),
        "best_format": best_result['format_name'] if best_result else None,
        "gpu_used": gpu_used,
        "memory_change": memory_change,
        "results": results
    }

def main():
    """主函数"""
    if len(sys.argv) < 2:
        logger.error("请提供图片路径！用法: python test_image_direct.py <图片路径>")
        return 1
    
    image_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        logger.error(f"图片不存在: {image_path}")
        return 1
    
    try:
        # 执行分析
        result = analyze_image_direct(image_path)
        return 0 if result.get("success") else 1
    except Exception as e:
        logger.exception(f"测试执行过程中出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 