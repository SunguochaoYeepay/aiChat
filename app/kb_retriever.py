import os
from pathlib import Path
from typing import List, Dict
import markdown
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import KB_DIR, KB_EXTENSIONS

class KnowledgeBase:
    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.load_documents()

    def load_documents(self):
        """加载知识库中的所有文档"""
        for file in KB_DIR.glob("**/*"):
            if file.suffix in KB_EXTENSIONS:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.documents[file.stem] = content

    def search(self, topic: str, query: str) -> str:
        """在指定话题的文档中搜索相关内容"""
        if topic not in self.documents:
            return f"未找到话题 '{topic}' 的相关文档"
        
        # 这里可以添加更复杂的搜索逻辑
        # 目前只是简单返回整个文档
        return self.documents[topic]

    def refresh(self):
        """刷新知识库"""
        self.documents.clear()
        self.load_documents()
        return "知识库已刷新" 