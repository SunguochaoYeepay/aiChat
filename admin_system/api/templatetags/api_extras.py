import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def pprint(value):
    """格式化输出JSON数据"""
    if not value:
        return "无数据"
    
    try:
        # 如果是字符串，尝试解析为JSON
        if isinstance(value, str):
            json_value = json.loads(value)
        else:
            json_value = value
            
        # 格式化输出
        formatted = json.dumps(json_value, ensure_ascii=False, indent=2)
        return mark_safe(formatted)
    except Exception as e:
        # 如果解析失败，直接返回原始值
        return str(value) 