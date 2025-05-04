"""
测试模型状态API
"""
import requests
import json
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_model_status(base_url="http://localhost:8000"):
    """
    测试模型状态API
    
    Args:
        base_url: API基础URL
    """
    # 组合完整URL
    url = f"{base_url}/api/status"
    
    logger.info(f"正在测试模型状态API: {url}")
    
    try:
        # 发送GET请求
        response = requests.get(url, timeout=10)
        
        # 检查响应状态
        logger.info(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 尝试解析JSON响应
            try:
                result = response.json()
                
                # 打印服务状态信息
                logger.info(f"服务状态: {result.get('status', 'unknown')}")
                logger.info(f"消息: {result.get('message', 'unknown')}")
                logger.info(f"模型已加载: {result.get('model_loaded', False)}")
                logger.info(f"GPU可用: {result.get('gpu_available', False)}")
                
                # 验证是否模型已加载
                if result.get('model_loaded', False):
                    logger.info("测试成功: 模型已加载")
                    return True
                else:
                    logger.warning("测试失败: 模型未加载")
                    return False
                
            except json.JSONDecodeError as e:
                logger.error(f"解析响应时出错: {str(e)}")
                logger.error(f"原始响应内容:\n{response.text}")
                return False
        else:
            logger.error(f"请求失败，状态码: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return False
        
    except requests.RequestException as e:
        logger.exception(f"请求异常: {str(e)}")
        return False

if __name__ == "__main__":
    # 从命令行参数获取URL或使用默认值
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = test_model_status(base_url)
    
    # 设置退出码
    sys.exit(0 if success else 1) 
 