"""
API应用配置 - 定义API应用的配置信息
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API兼容层'
    
    def ready(self):
        """应用就绪时的初始化操作"""
        # 确保加载信号处理器和其他需要在应用启动时初始化的内容
        pass 