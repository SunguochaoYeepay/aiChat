"""
模型加载脚本 - 确保模型完全加载并服务正常运行
此脚本发送适当的请求以触发模型完全加载，并验证模型是否正确加载
"""
import requests
import json
import time
import sys
import logging
import os

# 设置日志文件
LOG_FILE = "model_startup.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def wait_for_service(base_url, max_retries=30, retry_interval=1):
    """等待服务启动"""
    logger.info(f"等待API服务启动 {base_url}...")
    
    for i in range(max_retries):
        try:
            resp = requests.get(f"{base_url}/api/status", timeout=3)
            if resp.status_code == 200:
                logger.info("API服务已启动")
                return True
        except Exception as e:
            if i % 5 == 0:  # 每5次重试记录一次日志
                logger.info(f"等待服务启动中... ({i+1}/{max_retries})")
            
        time.sleep(retry_interval)
        
    logger.error(f"等待API服务启动超时，已尝试 {max_retries} 次")
    return False

def trigger_model_load(port=8001, max_attempts=3, timeout=180):
    """
    发送请求触发模型加载并监控状态
    
    Args:
        port: API服务端口
        max_attempts: 最大尝试次数
        timeout: 等待模型加载的超时时间(秒)
        
    Returns:
        bool: 是否成功加载模型
    """
    base_url = f"http://127.0.0.1:{port}"
    
    # 1. 等待服务启动
    if not wait_for_service(base_url):
        return False
        
    # 2. 检查初始状态
    logger.info("检查初始模型状态...")
    try:
        status_resp = requests.get(f"{base_url}/api/status")
        status = status_resp.json()
        
        if status.get("model_loaded", False):
            logger.info("模型已加载，无需触发")
            return True
            
        logger.info(f"当前服务状态: {json.dumps(status, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"检查状态时出错: {str(e)}")
    
    # 3. 发送触发请求
    for attempt in range(1, max_attempts + 1):
        logger.info(f"尝试 {attempt}/{max_attempts} - 发送请求触发模型加载...")
        
        try:
            # 发送简单聊天请求
            chat_resp = requests.post(
                f"{base_url}/api/v1/chat/completions",
                json={"messages": [{"role": "user", "content": "测试"}], "max_tokens": 5},
                timeout=30
            )
            
            logger.info(f"请求已发送，状态码: {chat_resp.status_code}")
            
            # 检查响应
            if chat_resp.status_code == 200:
                logger.info("请求成功，模型应该已开始加载")
            else:
                logger.warning(f"请求未成功，响应: {chat_resp.text}")
                
            # 等待并监控模型加载状态
            logger.info(f"等待模型加载完成(最多 {timeout} 秒)...")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    status_resp = requests.get(f"{base_url}/api/status", timeout=5)
                    if status_resp.status_code == 200:
                        status = status_resp.json()
                        
                        # 输出加载状态
                        if time.time() - start_time > 10:  # 10秒后开始定期输出状态
                            elapsed = int(time.time() - start_time)
                            if elapsed % 10 == 0:  # 每10秒输出一次状态
                                logger.info(f"已等待 {elapsed} 秒... 当前状态: {status.get('status', 'unknown')}")
                        
                        if status.get("model_loaded", False):
                            logger.info("成功！模型已完全加载")
                            return True
                        
                except Exception as e:
                    logger.warning(f"检查状态时出错: {str(e)}")
                    
                time.sleep(2)
                
            logger.warning(f"等待模型加载超时({timeout}秒)")
                
            # 清除模型缓存，尝试重置模型状态
            if attempt < max_attempts:
                logger.info("尝试清除缓存并重试...")
                try:
                    requests.post(f"{base_url}/api/reset_model", timeout=5)
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"重置模型时出错: {str(e)}")
                
        except Exception as e:
            logger.error(f"发送请求出错: {str(e)}")
            
        if attempt < max_attempts:
            logger.info(f"等待10秒后重试...")
            time.sleep(10)
    
    logger.error("无法触发模型加载，已达到最大尝试次数")
    return False

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("模型加载脚本开始执行")
    logger.info("=" * 50)
    
    # 获取端口参数
    port = 8001
    timeout = 180  # 默认等待3分钟
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"无效的端口参数: {sys.argv[1]}，使用默认端口8001")
    
    if len(sys.argv) > 2:
        try:
            timeout = int(sys.argv[2])
        except ValueError:
            logger.error(f"无效的超时参数: {sys.argv[2]}，使用默认超时180秒")
    
    logger.info(f"使用端口: {port}, 超时: {timeout}秒")
    
    # 执行模型加载
    if trigger_model_load(port, timeout=timeout):
        logger.info("=" * 50)
        logger.info("模型加载脚本执行成功！")
        logger.info("=" * 50)
        sys.exit(0)
    else:
        logger.error("=" * 50)
        logger.error("模型加载脚本执行失败！")
        logger.error("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main() 