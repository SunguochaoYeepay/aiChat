import requests
import json
from typing import Dict, Any, Union, List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import QWEN_API_URL, QWEN_API_KEY

class QwenAPI:
    def __init__(self):
        self.api_url = QWEN_API_URL
        self.headers = {
            "Content-Type": "application/json",
        }
        if QWEN_API_KEY:
            self.headers["Authorization"] = f"Bearer {QWEN_API_KEY}"

    def analyze_image(self, topic: str, image_base64: Union[str, List[str]], question: str) -> str:
        """分析图片并回答问题，支持单张或多张图片"""
        # 构建请求数据
        data = {
            "image_base64": image_base64,  # 直接传递，后端会处理单张或多张
            "query": f"请分析这张{topic}的图片，并回答以下问题：{question}"
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["result"]  # 返回分析结果
        except Exception as e:
            return f"API调用失败: {str(e)}" 