"""
ASGI config for admin_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import sys
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

# 确保应用路径正确
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')

# 获取Django ASGI应用
django_asgi_app = get_asgi_application()

# 导入WebSocket消费者
from api.websocket import ChatConsumer, AnalyzeConsumer

# 定义WebSocket路由
websocket_urlpatterns = [
    path('ws/chat', ChatConsumer.as_asgi()),
    path('ws/analyze', AnalyzeConsumer.as_asgi()),
]

# 配置ASGI应用
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
