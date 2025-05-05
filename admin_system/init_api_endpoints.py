import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()

from api.models import APIEndpoint

# 定义初始API端点数据
initial_endpoints = [
    {
        'name': '图像分析接口',
        'description': '分析图像并根据查询提供结果',
        'path': '/analyze',
        'method': 'POST',
        'status': 'active',
        'permission': 'authenticated',
        'request_schema': {
            'type': 'object',
            'properties': {
                'image_base64': {
                    'type': 'string',
                    'description': '图像的Base64编码'
                },
                'query': {
                    'type': 'string',
                    'description': '查询文本'
                }
            },
            'required': ['image_base64', 'query']
        },
        'response_schema': {
            'type': 'object',
            'properties': {
                'result': {
                    'type': 'string',
                    'description': '分析结果'
                }
            }
        },
        'version': '1.0'
    },
    {
        'name': '聊天完成接口',
        'description': '提供聊天完成功能',
        'path': '/v1/chat/completions',
        'method': 'POST',
        'status': 'active',
        'permission': 'authenticated',
        'request_schema': {
            'type': 'object',
            'properties': {
                'messages': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'role': {
                                'type': 'string',
                                'enum': ['system', 'user', 'assistant']
                            },
                            'content': {
                                'type': 'string'
                            }
                        }
                    }
                },
                'stream': {
                    'type': 'boolean',
                    'default': False
                }
            },
            'required': ['messages']
        },
        'response_schema': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'string'
                },
                'object': {
                    'type': 'string'
                },
                'choices': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'index': {
                                'type': 'integer'
                            },
                            'message': {
                                'type': 'object',
                                'properties': {
                                    'role': {
                                        'type': 'string'
                                    },
                                    'content': {
                                        'type': 'string'
                                    }
                                }
                            },
                            'finish_reason': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        },
        'version': '1.0'
    },
    {
        'name': '知识库搜索接口',
        'description': '搜索知识库内容',
        'path': '/search',
        'method': 'POST',
        'status': 'active',
        'permission': 'authenticated',
        'request_schema': {
            'type': 'object',
            'properties': {
                'query': {
                    'type': 'string',
                    'description': '搜索查询'
                },
                'top_k': {
                    'type': 'integer',
                    'description': '返回结果数量',
                    'default': 5
                }
            },
            'required': ['query']
        },
        'response_schema': {
            'type': 'object',
            'properties': {
                'results': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'integer'
                            },
                            'name': {
                                'type': 'string'
                            },
                            'content': {
                                'type': 'string'
                            },
                            'similarity': {
                                'type': 'number'
                            }
                        }
                    }
                },
                'count': {
                    'type': 'integer'
                }
            }
        },
        'version': '1.0'
    },
    {
        'name': '服务状态接口',
        'description': '获取服务运行状态信息',
        'path': '/status',
        'method': 'GET',
        'status': 'active',
        'permission': 'public',
        'response_schema': {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'enum': ['running', 'maintenance', 'error']
                },
                'version': {
                    'type': 'string'
                },
                'uptime': {
                    'type': 'number'
                },
                'message': {
                    'type': 'string'
                }
            }
        },
        'version': '1.0'
    }
]

def init_api_endpoints():
    """初始化API端点数据"""
    created_count = 0
    skipped_count = 0
    
    for endpoint_data in initial_endpoints:
        # 检查是否已存在
        exists = APIEndpoint.objects.filter(
            path=endpoint_data['path'],
            method=endpoint_data['method'],
            version=endpoint_data['version']
        ).exists()
        
        if not exists:
            # 创建新的API端点
            endpoint = APIEndpoint(**endpoint_data)
            endpoint.save()
            created_count += 1
            print(f"创建API端点: {endpoint.method} {endpoint.path}")
        else:
            skipped_count += 1
            print(f"跳过已存在的API端点: {endpoint_data['method']} {endpoint_data['path']}")
    
    print(f"\n完成初始化! 创建了 {created_count} 个新API端点, 跳过了 {skipped_count} 个已存在的API端点。")

if __name__ == '__main__':
    print("开始初始化API端点...")
    init_api_endpoints() 