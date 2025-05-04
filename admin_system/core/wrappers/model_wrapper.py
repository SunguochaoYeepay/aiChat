# -*- coding: utf-8 -*-
"""
模型包装器模块 - 提供统一的模型接口

此模块封装了模型加载和使用的功能，简化调用过程。
"""

import torch
import logging
import traceback
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import os

# 设置日志
logger = logging.getLogger(__name__)

class ModelWrapper:
    """
    模型包装器类 - 用于加载和使用量化模型
    
    此类提供了一个统一的接口来加载和使用各种模型，
    特别是针对需要特殊处理的量化模型（如GPTQ格式）。
    """
    
    def __init__(self, model_path, device=None, precision="float16"):
        self.model_path = model_path
        self.device = device if device else "cuda" if torch.cuda.is_available() else "cpu"
        self.precision = precision
        self.torch_dtype = torch.float16 if precision == "float16" else torch.float32
        
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
        logger.info(f"创建ModelWrapper实例: 路径={model_path}, 设备={self.device}, 精度={precision}")
    
    def load(self):
        """
        加载模型和tokenizer
        
        Returns:
            dict: 加载状态
        """
        try:
            # 加载tokenizer
            logger.info("加载tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            logger.info("tokenizer加载成功")
            
            # 加载model
            logger.info("加载model...")
            
            # 判断是否使用量化模型
            is_int4_model = "Int4" in self.model_path
            is_int8_model = "Int8" in self.model_path
            
            # 检查是否是量化模型但CUDA不可用
            if (is_int4_model or is_int8_model) and self.device == 'cpu':
                logger.warning("检测到尝试在CPU上加载量化模型，量化模型需要GPU支持")
                logger.warning("正在尝试在CPU上加载标准模型...")
                
                # 尝试寻找非量化版本的模型
                non_quantized_path = self.model_path.replace("-Int4", "").replace("-Int8", "")
                if os.path.exists(non_quantized_path):
                    logger.info(f"找到非量化模型: {non_quantized_path}，尝试加载...")
                    self.model_path = non_quantized_path
                else:
                    return {
                        'status': 'error',
                        'message': '量化模型需要GPU支持，且未找到对应的非量化模型。请使用带GPU的环境或提供非量化模型路径'
                    }
            
            try:
                # 尝试加载模型
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map=self.device,
                    trust_remote_code=True,
                    bf16=(self.precision == 'bfloat16'),
                    fp16=(self.precision == 'float16')
                ).eval()
                logger.info("model加载成功")
            except RuntimeError as e:
                if "GPU is required" in str(e) and self.device == 'cuda':
                    # GPU需要但不可用，尝试回退到CPU
                    logger.warning(f"GPU加载失败: {e}")
                    logger.warning("尝试回退到CPU模式")
                    self.device = 'cpu'
                    
                    # 检查是否是量化模型
                    if is_int4_model or is_int8_model:
                        # 量化模型无法在CPU上运行，查找非量化版本
                        non_quantized_path = self.model_path.replace("-Int4", "").replace("-Int8", "")
                        if os.path.exists(non_quantized_path):
                            logger.info(f"找到非量化模型: {non_quantized_path}，尝试加载...")
                            self.model_path = non_quantized_path
                        else:
                            logger.error("未找到非量化模型，无法在CPU上加载量化模型")
                            raise RuntimeError("量化模型需要GPU支持，且未找到对应的非量化模型")
                    
                    # 重新尝试用CPU加载
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        device_map=self.device,
                        trust_remote_code=True
                    ).eval()
                    logger.info("model已在CPU上加载成功")
                else:
                    # 其他错误，重新抛出
                    raise
            
            # 配置生成参数
            self.model.generation_config = GenerationConfig.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            return {
                'status': 'success',
                'message': f'模型加载成功: {self.model_path}'
            }
            
        except Exception as e:
            logger.error(f"model加载失败: {str(e)}")
            # 记录详细错误堆栈
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'message': f'模型加载失败: {str(e)}'
            }
    
    def chat(self, prompt, history=None):
        """
        进行对话
        
        Args:
            prompt: 用户输入的提示文本
            history: 对话历史记录
            
        Returns:
            tuple: (回复文本, 新的历史记录)
        """
        # 确保模型已加载
        if not self.is_loaded:
            logger.warning("模型未加载，尝试加载...")
            if not self.load():
                return "模型加载失败，无法生成回复", history or []
        
        if history is None:
            history = []
        
        try:
            logger.info(f"生成回复，提示词长度: {len(prompt)}, 历史记录: {len(history)}条")
            # 调用模型的chat方法
            response, new_history = self.model.chat(self.tokenizer, prompt, history=history)
            logger.info(f"回复生成成功，长度: {len(response)}")
            return response, new_history
        except Exception as e:
            error_msg = f"聊天生成出错: {str(e)}"
            logger.exception(error_msg)
            logger.error(f"异常堆栈: {traceback.format_exc()}")
            return f"抱歉，生成回复时出错: {str(e)}", history
    
    def generate(self, prompt):
        """
        简单的生成函数，不使用历史记录
        
        Args:
            prompt: 用户输入的提示文本
            
        Returns:
            str: 生成的响应文本
        """
        return self.chat(prompt)[0]
