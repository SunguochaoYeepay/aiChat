"""
提示词模板管理器
"""
import logging
from django.core.cache import cache
from typing import Dict, Optional
from .models import PromptTemplate

logger = logging.getLogger(__name__)

class PromptManager:
    """提示词模板管理器"""
    
    def __init__(self):
        """初始化提示词模板管理器"""
        self.cache_key = 'prompt_templates'
        self.templates = {}
        self.refresh_cache()
    
    def refresh_cache(self) -> None:
        """刷新缓存"""
        try:
            # 从数据库加载所有模板
            templates = {}
            for template in PromptTemplate.objects.all():
                templates[template.name] = template.content
            
            # 更新缓存
            cache.set(self.cache_key, templates, timeout=86400)  # 24小时
            self.templates = templates
            
            logger.info(f"成功刷新提示词模板缓存，共 {len(templates)} 个模板")
        except Exception as e:
            logger.error(f"刷新提示词模板缓存出错: {str(e)}")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """
        获取提示词模板
        
        Args:
            template_name: 模板名称 (格式: category.type)
        
        Returns:
            模板内容，如果不存在则返回 None
        """
        # 先从缓存中获取
        if not self.templates:
            cached_templates = cache.get(self.cache_key)
            if cached_templates:
                self.templates = cached_templates
            else:
                self.refresh_cache()
        
        return self.templates.get(template_name)
    
    def get_templates_by_category(self, category: str) -> Dict[str, str]:
        """
        按分类获取提示词模板
        
        Args:
            category: 模板分类
        
        Returns:
            {type: content} 格式的字典
        """
        result = {}
        prefix = f"{category}."
        
        for name, content in self.templates.items():
            if name.startswith(prefix):
                type_name = name[len(prefix):]
                result[type_name] = content
        
        return result


# 单例实例
prompt_manager = PromptManager() 