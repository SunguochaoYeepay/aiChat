"""
API端点初始化脚本

此脚本用于初始化系统中所有对外提供的API端点数据
"""
import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()

# 导入API模型
from api.models import APIEndpoint

def init_api_endpoints():
    """初始化API端点数据"""
    print("开始初始化API端点数据...")
    
    # 定义默认API端点数据
    default_endpoints = [
        {
            "name": "聊天完成",
            "path": "/api/v1/chat/completions",
            "method": "POST",
            "description": "发送消息到模型并获取聊天回复",
            "status": "active",
            "permission": "authenticated",
            "request_schema": {
                "messages": [
                    {"role": "system", "content": "你是一个AI助手"},
                    {"role": "user", "content": "你好，请介绍一下自己"}
                ],
                "stream": False,
                "template_type": "general"
            },
            "response_schema": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677858242,
                "model": "gpt-3.5-turbo-0301",
                "usage": {
                    "prompt_tokens": 13,
                    "completion_tokens": 7,
                    "total_tokens": 20
                },
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "我是一个AI助手，可以帮助你回答问题、提供信息和完成各种任务。"
                        },
                        "finish_reason": "stop",
                        "index": 0
                    }
                ]
            }
        },
        {
            "name": "分析图像",
            "path": "/api/analyze",
            "method": "POST",
            "description": "分析图像并获取描述",
            "status": "active",
            "permission": "authenticated",
            "request_schema": {
                "image_base64": "base64编码的图像数据",
                "query": "描述这张图片",
                "template_type": "general"
            },
            "response_schema": {
                "text": "这是一张图片的详细描述...",
                "processing_time": 1.23
            }
        },
        {
            "name": "知识库搜索",
            "path": "/api/search",
            "method": "POST",
            "description": "在知识库中搜索相关内容",
            "status": "active",
            "permission": "authenticated",
            "request_schema": {
                "query": "如何使用知识库搜索功能?",
                "top_k": 5
            },
            "response_schema": {
                "results": [
                    {
                        "id": 1,
                        "name": "知识库项目名称",
                        "content": "匹配的内容片段...",
                        "similarity": 0.92
                    }
                ],
                "count": 1
            }
        },
        {
            "name": "获取服务状态",
            "path": "/api/status",
            "method": "GET",
            "description": "获取系统服务状态",
            "status": "active",
            "permission": "public",
            "request_schema": {},
            "response_schema": {
                "status": "running",
                "model_loaded": True,
                "uptime": 3600,
                "version": "1.0.0"
            }
        },
        {
            "name": "获取API端点列表",
            "path": "/api/v1/endpoints",
            "method": "GET",
            "description": "获取所有可用的API端点信息",
            "status": "active",
            "permission": "authenticated",
            "request_schema": {},
            "response_schema": {
                "endpoints": [
                    {
                        "id": 1,
                        "name": "API名称",
                        "path": "/api/path",
                        "method": "GET",
                        "description": "API描述"
                    }
                ]
            }
        },
        {
            "name": "获取API密钥列表",
            "path": "/api/v1/api-keys",
            "method": "GET",
            "description": "获取所有API密钥信息",
            "status": "active",
            "permission": "admin",
            "request_schema": {},
            "response_schema": {
                "api_keys": [
                    {
                        "id": 1,
                        "name": "密钥名称",
                        "key": "sk-...",
                        "is_active": True,
                        "created_at": "2023-04-01T12:00:00Z"
                    }
                ]
            }
        },
        {
            "name": "创建API密钥",
            "path": "/api/v1/api-keys/create",
            "method": "POST",
            "description": "创建新的API密钥",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "name": "密钥名称",
                "description": "密钥描述",
                "expires_at": "2023-12-31T23:59:59Z"
            },
            "response_schema": {
                "id": 1,
                "name": "密钥名称",
                "key": "sk-...",
                "is_active": True,
                "created_at": "2023-04-01T12:00:00Z"
            }
        },
        {
            "name": "更新API密钥",
            "path": "/api/v1/api-keys/{key_id}/update",
            "method": "PUT",
            "description": "更新指定的API密钥",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "name": "新密钥名称",
                "description": "新密钥描述",
                "is_active": False
            },
            "response_schema": {
                "id": 1,
                "name": "新密钥名称",
                "is_active": False,
                "updated_at": "2023-04-01T12:00:00Z"
            }
        },
        {
            "name": "删除API密钥",
            "path": "/api/v1/api-keys/{key_id}/delete",
            "method": "DELETE",
            "description": "删除指定的API密钥",
            "status": "active",
            "permission": "admin",
            "request_schema": {},
            "response_schema": {
                "message": "API密钥已成功删除"
            }
        },
        {
            "name": "用户登录",
            "path": "/api/auth/login/",
            "method": "POST",
            "description": "用户登录并获取认证",
            "status": "active",
            "permission": "public",
            "request_schema": {
                "username": "用户名",
                "password": "密码"
            },
            "response_schema": {
                "status": "success",
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "is_staff": True
                }
            }
        },
        {
            "name": "用户退出",
            "path": "/api/auth/logout/",
            "method": "POST",
            "description": "用户退出登录",
            "status": "active",
            "permission": "authenticated",
            "request_schema": {},
            "response_schema": {
                "status": "success",
                "message": "退出登录成功"
            }
        },
        {
            "name": "获取当前用户信息",
            "path": "/api/auth/user/",
            "method": "GET",
            "description": "获取当前登录用户信息",
            "status": "active",
            "permission": "authenticated",
            "request_schema": {},
            "response_schema": {
                "status": "success",
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "is_staff": True
                }
            }
        },
        {
            "name": "获取用户列表",
            "path": "/api/auth/users/",
            "method": "GET",
            "description": "获取所有用户列表（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {},
            "response_schema": {
                "users": [
                    {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "is_active": True,
                        "is_staff": True
                    }
                ]
            }
        },
        {
            "name": "创建用户",
            "path": "/api/auth/users/create/",
            "method": "POST",
            "description": "创建新用户（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "username": "新用户名",
                "email": "user@example.com",
                "password": "密码",
                "is_staff": False
            },
            "response_schema": {
                "status": "success",
                "user": {
                    "id": 2,
                    "username": "新用户名",
                    "email": "user@example.com",
                    "is_staff": False
                }
            }
        },
        {
            "name": "更新用户",
            "path": "/api/auth/users/{user_id}/update/",
            "method": "PUT",
            "description": "更新指定用户信息（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "username": "更新的用户名",
                "email": "updated@example.com",
                "is_active": False
            },
            "response_schema": {
                "status": "success",
                "user": {
                    "id": 2,
                    "username": "更新的用户名",
                    "email": "updated@example.com",
                    "is_active": False
                }
            }
        },
        {
            "name": "删除用户",
            "path": "/api/auth/users/{user_id}/delete/",
            "method": "DELETE",
            "description": "删除指定用户（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {},
            "response_schema": {
                "status": "success",
                "message": "用户已删除"
            }
        },
        {
            "name": "创建API端点",
            "path": "/api/v1/endpoints/create",
            "method": "POST",
            "description": "创建新的API端点（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "name": "API名称",
                "path": "/api/path",
                "method": "GET",
                "description": "API描述",
                "status": "active",
                "permission": "public"
            },
            "response_schema": {
                "id": 1,
                "name": "API名称",
                "path": "/api/path",
                "method": "GET",
                "description": "API描述",
                "status": "active",
                "permission": "public",
                "created_at": "2023-04-01T12:00:00Z"
            }
        },
        {
            "name": "更新API端点",
            "path": "/api/v1/endpoints/{endpoint_id}/update",
            "method": "PUT",
            "description": "更新指定的API端点（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "name": "更新的API名称",
                "path": "/api/new-path",
                "status": "deprecated"
            },
            "response_schema": {
                "id": 1,
                "name": "更新的API名称",
                "path": "/api/new-path",
                "method": "GET",
                "status": "deprecated",
                "updated_at": "2023-04-01T12:00:00Z"
            }
        },
        {
            "name": "删除API端点",
            "path": "/api/v1/endpoints/{endpoint_id}/delete",
            "method": "DELETE",
            "description": "删除指定的API端点（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {},
            "response_schema": {
                "message": "API端点已成功删除",
                "id": 1
            }
        },
        {
            "name": "执行API测试",
            "path": "/api/test/execute/",
            "method": "POST",
            "description": "执行API接口测试（仅管理员可用）",
            "status": "active",
            "permission": "admin",
            "request_schema": {
                "endpoint_id": 1,
                "api_key": "可选的API密钥",
                "request_body": "{\"example\": \"data\"}"
            },
            "response_schema": {
                "result": "测试结果内容"
            }
        }
    ]
    
    # 计数器
    created_count = 0
    skipped_count = 0
    
    # 遍历并创建/更新API端点
    for endpoint_data in default_endpoints:
        # 检查是否已存在
        existing = APIEndpoint.objects.filter(
            path=endpoint_data["path"], 
            method=endpoint_data["method"]
        ).first()
        
        if existing:
            print(f"跳过已存在的API端点: {endpoint_data['method']} {endpoint_data['path']}")
            skipped_count += 1
            continue
        
        # 创建新的API端点
        endpoint = APIEndpoint(
            name=endpoint_data["name"],
            path=endpoint_data["path"],
            method=endpoint_data["method"],
            description=endpoint_data.get("description", ""),
            status=endpoint_data.get("status", "active"),
            permission=endpoint_data.get("permission", "authenticated"),
            request_schema=endpoint_data.get("request_schema", {}),
            response_schema=endpoint_data.get("response_schema", {}),
            version=endpoint_data.get("version", "1.0"),
            rate_limit=endpoint_data.get("rate_limit", 60)
        )
        endpoint.save()
        created_count += 1
        print(f"已创建API端点: {endpoint_data['method']} {endpoint_data['path']}")
    
    print(f"API端点初始化完成。新建: {created_count}, 跳过: {skipped_count}")
    return created_count, skipped_count

if __name__ == "__main__":
    init_api_endpoints() 