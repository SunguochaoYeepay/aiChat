"""
WebSocket接口测试模块

此模块包含WebSocket接口的测试用例。
"""
import websocket
import json
import time
import sys
import threading
import logging
import ssl

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局变量用于接收消息
received_messages = []
connection_closed = False

def on_message(ws, message):
    """处理接收到的消息"""
    global received_messages
    logger.info(f"接收到消息: {message}")
    try:
        data = json.loads(message)
        received_messages.append(data)
    except json.JSONDecodeError:
        logger.error(f"无法解析JSON消息: {message}")

def on_error(ws, error):
    """处理错误"""
    logger.error(f"WebSocket错误: {error}")

def on_close(ws, close_status_code, close_msg):
    """处理连接关闭"""
    global connection_closed
    connection_closed = True
    logger.info(f"WebSocket连接关闭: {close_status_code}, {close_msg}")

def on_open(ws):
    """处理连接打开"""
    logger.info("WebSocket连接已打开")

def test_chat_websocket(base_url="localhost:8000", timeout=30):
    """
    测试聊天WebSocket接口
    
    Args:
        base_url: WebSocket服务器地址
        timeout: 超时时间(秒)
    """
    global received_messages, connection_closed
    received_messages = []
    connection_closed = False
    
    # WebSocket URL
    ws_url = f"ws://{base_url}/ws/chat/"
    
    logger.info(f"测试聊天WebSocket接口: {ws_url}")
    
    # 创建WebSocket连接
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 在后台线程中运行WebSocket连接
    wst = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
    wst.daemon = True
    wst.start()
    
    # 等待连接打开
    time.sleep(2)
    
    try:
        # 发送聊天消息
        chat_message = {
            "type": "message",
            "message": {
                "role": "user",
                "content": "你好，这是一个测试消息。"
            }
        }
        
        logger.info(f"发送消息: {json.dumps(chat_message, ensure_ascii=False)}")
        ws.send(json.dumps(chat_message))
        
        # 等待响应
        start_time = time.time()
        while len(received_messages) == 0:
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                logger.error(f"等待响应超时({timeout}秒)")
                return False
        
        # 验证响应
        if len(received_messages) > 0:
            response = received_messages[0]
            logger.info(f"收到有效响应: {json.dumps(response, ensure_ascii=False)}")
            return True
        else:
            logger.error("未收到响应")
            return False
    
    except Exception as e:
        logger.exception(f"测试过程中出错: {str(e)}")
        return False
    
    finally:
        # 关闭WebSocket连接
        ws.close()
        
        # 等待连接关闭
        close_start_time = time.time()
        while not connection_closed:
            time.sleep(0.5)
            if time.time() - close_start_time > 5:  # 最多等待5秒
                logger.warning("WebSocket连接未正常关闭")
                break

def test_analyze_websocket(base_url="localhost:8000", timeout=30):
    """
    测试图像分析WebSocket接口
    
    Args:
        base_url: WebSocket服务器地址
        timeout: 超时时间(秒)
    """
    global received_messages, connection_closed
    received_messages = []
    connection_closed = False
    
    # WebSocket URL
    ws_url = f"ws://{base_url}/ws/analyze/"
    
    logger.info(f"测试图像分析WebSocket接口: {ws_url}")
    
    # 创建WebSocket连接
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 在后台线程中运行WebSocket连接
    wst = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
    wst.daemon = True
    wst.start()
    
    # 等待连接打开
    time.sleep(2)
    
    try:
        # 准备一个简单的测试图像的base64编码
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
        # 发送图像分析请求
        analyze_message = {
            "type": "analyze",
            "data": {
                "image_base64": test_image_base64,
                "query": "这是什么图片?"
            }
        }
        
        logger.info("发送图像分析请求...")
        ws.send(json.dumps(analyze_message))
        
        # 等待响应
        start_time = time.time()
        while len(received_messages) == 0:
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                logger.error(f"等待响应超时({timeout}秒)")
                return False
        
        # 验证响应
        if len(received_messages) > 0:
            response = received_messages[0]
            logger.info(f"收到有效响应: {json.dumps(response, ensure_ascii=False)}")
            return True
        else:
            logger.error("未收到响应")
            return False
    
    except Exception as e:
        logger.exception(f"测试过程中出错: {str(e)}")
        return False
    
    finally:
        # 关闭WebSocket连接
        ws.close()
        
        # 等待连接关闭
        close_start_time = time.time()
        while not connection_closed:
            time.sleep(0.5)
            if time.time() - close_start_time > 5:  # 最多等待5秒
                logger.warning("WebSocket连接未正常关闭")
                break

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "localhost:8000"
    
    # 测试聊天WebSocket接口
    logger.info("开始测试聊天WebSocket接口...")
    chat_success = test_chat_websocket(base_url)
    
    # 测试图像分析WebSocket接口
    logger.info("\n开始测试图像分析WebSocket接口...")
    analyze_success = test_analyze_websocket(base_url)
    
    # 输出测试结果
    if chat_success:
        logger.info("聊天WebSocket接口测试成功")
    else:
        logger.error("聊天WebSocket接口测试失败")
    
    if analyze_success:
        logger.info("图像分析WebSocket接口测试成功")
    else:
        logger.error("图像分析WebSocket接口测试失败")
    
    # 设置退出码
    sys.exit(0 if chat_success and analyze_success else 1) 