import os
import json
import re
from app.config import PROMPT_TEMPLATES_FILE, load_prompt_templates, DESIGN_KEYWORDS

class PromptManager:
    """提示词管理类，用于构建和管理提示词模板"""
    
    def __init__(self):
        # 加载提示词模板
        self.templates = load_prompt_templates()
        self.loaded = True if self.templates else False
    
    def refresh_templates(self):
        """刷新提示词模板"""
        self.templates = load_prompt_templates()
        self.loaded = True if self.templates else False
        return self.loaded
    
    def get_template(self, category, template_type):
        """获取特定类别和类型的提示词模板"""
        if not self.loaded:
            self.refresh_templates()
            
        if category in self.templates and template_type in self.templates[category]:
            return self.templates[category][template_type]
        return None
    
    def is_design_query(self, query):
        """判断查询是否与设计相关"""
        if not query:
            return False
        return any(keyword in query for keyword in DESIGN_KEYWORDS)
    
    def find_best_topic(self, query, topics):
        """根据查询内容找到最合适的知识库主题"""
        if not query or not topics:
            return "设计规范"  # 默认主题
            
        best_topic = None
        best_score = 0
        
        # 获取权重配置
        weights = self.templates.get("topic_matching", {}).get("score_weights", {"default": 1})
        
        for topic in topics:
            # 基础匹配分数
            score = sum(1 for word in query.split() if word in topic)
            
            # 应用特殊规则权重
            for pattern, weight in weights.items():
                if pattern == "default":
                    continue
                    
                keywords = pattern.split("_")
                if all(keyword in query for keyword in keywords) and topic in pattern:
                    score += weight
            
            if score > best_score:
                best_score = score
                best_topic = topic
        
        # 如果没有特定主题匹配，使用默认的"设计规范"
        if best_score == 0:
            return "设计规范"
            
        return best_topic
    
    def build_prompt(self, category, query, content=None, topic=None):
        """根据类别和查询构建提示词"""
        if not self.loaded:
            self.refresh_templates()
            
        # 如果与设计无关或没有内容，使用通用提示词
        if not self.is_design_query(query) or not content:
            template = self.get_template(category, "general")
            if not template:
                # 如果没有通用模板，返回原始查询
                return query
                
            return template.format(query=query)
        
        # 使用知识库提示词
        template = self.get_template(category, "knowledge_base")
        if not template:
            # 如果没有知识库模板，返回原始查询
            return query
            
        return template.format(topic=topic, content=content, query=query)
    
    def save_templates(self, templates):
        """保存提示词模板"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(PROMPT_TEMPLATES_FILE), exist_ok=True)
            
            # 保存模板
            with open(PROMPT_TEMPLATES_FILE, "w", encoding="utf-8") as f:
                json.dump(templates, f, ensure_ascii=False, indent=4)
                
            self.templates = templates
            self.loaded = True
            return True
        except Exception as e:
            print(f"保存提示词模板出错: {str(e)}")
            return False

# 创建全局提示词管理器实例
prompt_manager = PromptManager() 