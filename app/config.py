from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 知识库配置
KB_DIR = BASE_DIR / "knowledge_base"
KB_EXTENSIONS = [".md"]

# Qwen-VL-Chat API配置
QWEN_API_URL = "http://127.0.0.1:8000/analyze"  # 指向我们的本地 API 服务
QWEN_API_KEY = ""  # 本地服务不需要 API 密钥

# 服务器配置
HOST = "127.0.0.1"  # 只在本地访问
PORT = 8088  # 修改端口号，避免权限问题 