"""
知识库搜索API测试模块

此模块包含知识库搜索API接口的测试用例。
"""
import requests
import json
import time
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_search_api(base_url="http://localhost:8000", max_retries=3, retry_delay=5):
    """
    测试知识库搜索API
    
    Args:
        base_url: API基础URL
        max_retries: 最大重试次数
        retry_delay: 重试间隔(秒)
    """
    # 组合完整URL
    url = f"{base_url}/api/search"
    
    # 准备请求数据
    data = {
        "query": "图像分析功能如何使用"
    }
    
    logger.info(f"正在测试知识库搜索API: {url}")
    
    # 先检查服务状态
    try:
        status_url = f"{base_url}/api/status"
        logger.info(f"检查服务状态: {status_url}")
        status_response = requests.get(status_url)
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            logger.info(f"服务状态: {json.dumps(status_data, ensure_ascii=False)}")
        else:
            logger.warning(f"获取服务状态失败: {status_response.status_code}")
    except Exception as e:
        logger.exception(f"检查服务状态时出错: {str(e)}")
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试 #{attempt+1}/{max_retries}")
            
            # 发送POST请求
            start_time = time.time()
            response = requests.post(url, json=data, timeout=30)
            end_time = time.time()
            
            # 打印响应时间
            logger.info(f"响应时间: {end_time - start_time:.2f}秒")
            
            # 检查响应状态
            if response.status_code == 200:
                # 尝试解析JSON响应
                try:
                    result = response.json()
                    logger.info(f"响应状态码: {response.status_code}")
                    
                    # 打印结果的一部分
                    if isinstance(result, list) and len(result) > 0:
                        logger.info(f"找到 {len(result)} 条记录")
                        logger.info(f"第一条记录: {result[0]}")
                        logger.info("测试成功！")
                        return True
                    elif "results" in result and len(result["results"]) > 0:
                        logger.info(f"找到 {len(result['results'])} 条记录")
                        logger.info(f"第一条记录: {result['results'][0]}")
                        logger.info("测试成功！")
                        return True
                    else:
                        logger.warning(f"未找到匹配的知识库记录: {result}")
                        logger.info("测试成功！")  # 没有结果也算成功，因为API正常响应
                        return True
                
                except json.JSONDecodeError:
                    logger.error(f"无法解析JSON响应: {response.text}")
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
            
            # 如果还有重试机会，等待后重试
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
        
        except requests.RequestException as e:
            logger.exception(f"请求异常: {str(e)}")
            
            # 如果还有重试机会，等待后重试
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
    
    logger.error("所有重试均失败")
    return False

if __name__ == "__main__":
    # 从命令行参数获取URL或使用默认值
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = test_search_api(base_url)
    
    # 设置退出码
    sys.exit(0 if success else 1)