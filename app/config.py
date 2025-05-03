from pathlib import Path
import json
import os

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

# 提示词模板配置
PROMPT_TEMPLATES_FILE = BASE_DIR / "config" / "prompt_templates.json"

# 设计相关关键词
DESIGN_KEYWORDS = [
    "设计", "规范", "布局", "导航", "界面", "UI", "UX", 
    "用户体验", "交互", "颜色", "组件", "设计规范", 
    "间距", "登录页", "个人中心", "符合", "标准"
]

# 加载提示词模板
def load_prompt_templates():
    """加载提示词模板配置文件"""
    if not os.path.exists(PROMPT_TEMPLATES_FILE):
        # 如果配置文件不存在，创建默认配置
        default_templates = {
            "chat": {
                "knowledge_base": "以下是关于\"{topic}\"的设计规范文档:\n\n{content}\n\n请根据上述设计规范，回答用户的问题: {query}"
            },
            "image_analysis": {
                "knowledge_base": "以下是关于\"{topic}\"的设计规范文档:\n\n{content}\n\n请根据上述设计规范，分析图像并回答: {query}"
            },
            "search": {
                "knowledge_base": "以下是关于\"{topic}\"的设计规范文档:\n\n{content}\n\n请根据上述设计规范，回答用户的问题: {query}"
            }
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(PROMPT_TEMPLATES_FILE), exist_ok=True)
        
        # 保存默认配置
        with open(PROMPT_TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(default_templates, f, ensure_ascii=False, indent=4)
        
        return default_templates
    else:
        # 加载已有配置
        try:
            with open(PROMPT_TEMPLATES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载提示词模板配置出错: {str(e)}")
            return {} 