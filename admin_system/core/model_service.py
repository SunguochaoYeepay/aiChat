"""
模型服务模块 - 负责模型加载和管理

此模块提供模型加载、卸载、状态查询等核心功能，用于支持图像分析和文本生成。
"""
import os
import time
import torch
import logging
from django.conf import settings
from pathlib import Path

from .wrappers.model_wrapper import ModelWrapper

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量
model = None
tokenizer = None
model_wrapper = None
model_load_time = None
model_config = None
_is_loading = False  # 新增标志，防止并发加载

# 用于同步的锁对象
import threading
_model_lock = threading.Lock()

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
    global model, tokenizer, model_wrapper, model_load_time, model_config, _is_loading
    
    # 使用锁确保并发安全
    with _model_lock:
        # 如果正在加载中，则返回
        if _is_loading:
            return {
                'status': 'loading',
                'message': '模型正在加载中，请稍候'
            }
            
        _is_loading = True
        
        try:
            # 详细检查CUDA是否可用
            cuda_available = torch.cuda.is_available()
            logger.info(f"CUDA是否可用: {cuda_available}")
            if cuda_available:
                try:
                    cuda_device_count = torch.cuda.device_count()
                    cuda_device_name = torch.cuda.get_device_name(0) if cuda_device_count > 0 else "未知"
                    logger.info(f"CUDA设备数量: {cuda_device_count}, 设备名称: {cuda_device_name}")
                except Exception as e:
                    logger.warning(f"获取CUDA设备信息时出错: {str(e)}")
            
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
            
            # 检查CUDA是否可用，如果不可用则回退到CPU
            if device == 'cuda' and not cuda_available:
                logger.warning("CUDA不可用，回退到CPU模式运行")
                device = 'cpu'
                    
            logger.info(f"开始加载模型: {model_path}")
            logger.info(f"设备: {device}, 精度: {precision}")
            
            # 尝试查找非量化模型路径
            if device == 'cpu' and ('Int4' in model_path or 'Int8' in model_path):
                non_quantized_path = model_path.replace("-Int4", "").replace("-Int8", "")
                if os.path.exists(non_quantized_path):
                    logger.info(f"在CPU模式下使用非量化模型: {non_quantized_path}")
                    model_path = non_quantized_path
            
            # 记录加载开始时间
            load_start = time.time()
            
            # 创建模型包装器实例
            model_wrapper = ModelWrapper(model_path, device, precision)
            
            # 加载模型
            load_result = model_wrapper.load()
            
            if load_result.get('status') == 'success':
                # 设置全局变量
                model = model_wrapper.model
                tokenizer = model_wrapper.tokenizer
                
                # 计算加载时间
                model_load_time = time.time() - load_start
                
                logger.info(f"模型加载成功，耗时: {model_load_time:.2f}秒")
                
                # 测试模型是否可用
                test_result = test_model()
                if not test_result['success']:
                    logger.error(f"模型加载成功但测试失败: {test_result['message']}")
                    return {
                        'status': 'error',
                        'message': f'模型加载成功但测试失败: {test_result["message"]}'
                    }
                
                return {
                    'status': 'success',
                    'message': f'模型加载成功，耗时: {model_load_time:.2f}秒',
                    'model_path': model_path,
                    'device': device,
                    'precision': precision
                }
            else:
                logger.error(f"模型加载失败: {load_result.get('message', '未知错误')}")
                return {
                    'status': 'error',
                    'message': load_result.get('message', '模型加载失败，请查看日志获取详细信息')
                }
        except Exception as e:
            logger.exception(f"模型加载异常: {str(e)}")
            return {
                'status': 'error',
                'message': f'模型加载失败: {str(e)}'
            }
        finally:
            _is_loading = False

def test_model():
    """
    简单测试模型是否可用
    
    Returns:
        dict: 测试结果
    """
    global model, tokenizer
    
    if model is None or tokenizer is None:
        return {
            'success': False,
            'message': '模型或分词器为空'
        }
        
    try:
        # 简单的模型测试，尝试生成一个短文本
        result, _ = model.chat(tokenizer, "你好", history=[])
        
        if result and isinstance(result, str):
            return {
                'success': True,
                'message': '模型测试成功'
            }
        else:
            return {
                'success': False,
                'message': f'模型返回了意外的结果类型: {type(result)}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'模型测试时出错: {str(e)}'
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
    global _is_loading, model, tokenizer, model_wrapper
    
    # 如果正在加载，返回加载中状态
    if _is_loading:
        return {
            'status': 'loading',
            'message': '模型正在加载中，请稍候',
            'gpu_available': torch.cuda.is_available(),
            'model_loaded': False
        }
    
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
    获取模型实例，如果模型未加载则先加载模型
    
    Returns:
        tuple: (model, tokenizer)
    """
    global _is_loading, model, tokenizer
    
    # 如果模型已加载，直接返回
    if model is not None and tokenizer is not None:
        return model, tokenizer
    
    # 如果模型正在加载中，等待加载完成
    if _is_loading:
        logger.info("模型正在加载中，等待加载完成...")
        while _is_loading:
            time.sleep(0.5)
        return model, tokenizer
    
    # 开始加载模型
    _is_loading = True
    try:
        logger.info("模型未加载，开始加载...")
        
        # 获取配置
        model_path = getattr(settings, 'DEFAULT_MODEL_PATH', 'D:/AI-DEV/models/Qwen-VL-Chat')
        device = getattr(settings, 'DEFAULT_DEVICE', 'cuda')
        precision = getattr(settings, 'DEFAULT_PRECISION', 'float16')
        
        # 检查CUDA是否可用，如果不可用则回退到CPU
        if device == 'cuda' and not torch.cuda.is_available():
            logger.warning("CUDA不可用，回退到CPU模式运行")
            device = 'cpu'
            
        logger.info(f"开始加载模型: {model_path}")
        logger.info(f"设备: {device}, 精度: {precision}")
        
        # 创建模型包装器
        wrapper = ModelWrapper(model_path, device, precision)
        
        # 加载模型
        result = wrapper.load()
        logger.info(f"模型加载结果: {result}")
        
        if result.get('status') == 'success':
            model = wrapper.model
            tokenizer = wrapper.tokenizer
        else:
            logger.error("模型加载失败")
            
    except Exception as e:
        logger.exception(f"加载模型时出错: {str(e)}")
    finally:
        _is_loading = False
    
    if model is None:
        logger.error("模型加载失败，无法获取模型实例")
    
    return model, tokenizer
 