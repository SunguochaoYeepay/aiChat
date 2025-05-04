"""
工具函数模块 - 通用辅助功能

此模块提供通用的辅助功能，如配置加载、路径处理等。
"""
import os
import json
from django.conf import settings
from pathlib import Path

def get_static_dir():
    """获取静态文件目录"""
    static_dir = os.path.join(settings.BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)
    return static_dir

def get_box_image_dir():
    """获取边界框图像目录"""
    box_dir = os.path.join(get_static_dir(), 'box_images')
    os.makedirs(box_dir, exist_ok=True)
    return box_dir

def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
    return path

def get_file_extension(filename):
    """获取文件扩展名"""
    return os.path.splitext(filename)[1]

def load_json_file(file_path, default=None):
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
        default: 默认值，当文件不存在或加载失败时返回
        
    Returns:
        加载的JSON数据或默认值
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败 {file_path}: {e}")
    return default

def save_json_file(file_path, data):
    """
    保存JSON文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
        
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存JSON文件失败 {file_path}: {e}")
        return False 