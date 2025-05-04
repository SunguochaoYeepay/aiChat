"""
模型服务模块 - 负责模型加载和管理

此模块提供模型加载、卸载、状态查询等核心功能，用于支持图像分析和文本生成。
"""
import os
import time
import torch
from django.conf import settings
from pathlib import Path

# 全局变量
model = None
tokenizer = None
model_load_time = None
model_config = None

def init_model(model_path=None, device=None, precision=None):
    """
    初始化并加载模型
    
    Args:
        model_path: 模型路径
        device: 设备 ('cuda' 或 'cpu')
        precision: 精度 ('float16' 或 'float32')
    
    Returns:
        dict: 包含加载状态和时间的字典
    """
    global model, tokenizer, model_load_time, model_config
    
    # 如果没有提供配置，则使用默认值或从数据库获取
    if not model_path:
        from management.models import ModelConfig
        try:
            active_config = ModelConfig.objects.get(is_active=True)
            model_path = active_config.model_path
            device = active_config.device
            precision = active_config.precision
            model_config = active_config
        except ModelConfig.DoesNotExist:
            # 使用默认值
            model_path = getattr(settings, 'DEFAULT_MODEL_PATH', 'D:/AI-DEV/models/Qwen-VL-Chat-Int4')
            device = getattr(settings, 'DEFAULT_DEVICE', 'cuda')
            precision = getattr(settings, 'DEFAULT_PRECISION', 'float16')
    
    try:
        # 记录加载开始时间
        load_start = time.time()
        
        # 导入必要的库
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # 检查模型路径是否存在
        if not os.path.exists(model_path):
            return {
                'status': 'error',
                'message': f'模型路径不存在: {model_path}'
            }
        
        # 检查GPU可用性
        if device == 'cuda' and not torch.cuda.is_available():
            device = 'cpu'
            print("警告: GPU不可用，将使用CPU模式")
        
        # 确定torch数据类型
        torch_dtype = torch.float16 if precision == 'float16' else torch.float32
        
        # 加载tokenizer
        print(f"正在加载模型 {model_path}...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        
        # 加载模型
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_cache=True
        )
        
        # 将模型移至指定设备
        if device == 'cuda':
            model = model.to(device)
        
        # 将模型设置为评估模式
        model = model.eval()
        
        # 计算加载时间
        model_load_time = time.time() - load_start
        
        return {
            'status': 'success',
            'message': f'模型加载成功，耗时: {model_load_time:.2f}秒',
            'model_path': model_path,
            'device': device,
            'precision': precision
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'模型加载失败: {str(e)}'
        }

def reload_model(model_id=None):
    """
    重新加载模型
    
    Args:
        model_id: 模型配置ID
    
    Returns:
        dict: 加载状态
    """
    global model, tokenizer
    
    # 释放现有模型资源
    if model is not None:
        del model
        model = None
    
    if tokenizer is not None:
        del tokenizer
        tokenizer = None
    
    # 强制执行垃圾回收
    import gc
    gc.collect()
    
    # 如果GPU可用，清空GPU缓存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # 如果指定了model_id，加载指定的模型配置
    if model_id:
        from management.models import ModelConfig
        try:
            model_config = ModelConfig.objects.get(id=model_id)
            # 将其设为活动状态，并将其他模型设为非活动
            ModelConfig.objects.all().update(is_active=False)
            model_config.is_active = True
            model_config.save()
            
            return init_model(
                model_config.model_path,
                model_config.device,
                model_config.precision
            )
        except ModelConfig.DoesNotExist:
            return {
                'status': 'error',
                'message': f'模型配置不存在，ID: {model_id}'
            }
    else:
        # 加载当前活动的模型配置
        return init_model()

def get_service_status():
    """
    获取模型服务状态
    
    Returns:
        dict: 包含服务状态信息的字典
    """
    # 检查模型是否已加载
    if model is None or tokenizer is None:
        return {
            'status': 'stopped',
            'message': '模型未加载',
            'gpu_available': torch.cuda.is_available(),
            'model_loaded': False
        }
    
    # 获取设备信息
    device = next(model.parameters()).device
    device_name = str(device)
    
    # 如果在GPU上，获取GPU信息
    gpu_info = {}
    if device.type == 'cuda':
        gpu_info = {
            'name': torch.cuda.get_device_name(0),
            'total_memory': torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024,
            'allocated_memory': torch.cuda.memory_allocated(0) / 1024 / 1024 / 1024,
            'cached_memory': torch.cuda.memory_reserved(0) / 1024 / 1024 / 1024
        }
    
    return {
        'status': 'running',
        'message': '模型已加载并运行中',
        'model_loaded': True,
        'device': device_name,
        'load_time': model_load_time,
        'gpu_available': torch.cuda.is_available(),
        'gpu_info': gpu_info,
        'model_config': {
            'path': model_config.model_path if model_config else 'unknown',
            'device': model_config.device if model_config else device_name,
            'precision': model_config.precision if model_config else 'unknown'
        } if model_config else {}
    }

def get_model():
    """
    获取模型实例
    
    Returns:
        tuple: (model, tokenizer) 元组
    """
    # 如果模型未加载，则加载模型
    if model is None or tokenizer is None:
        init_model()
        
    return model, tokenizer 