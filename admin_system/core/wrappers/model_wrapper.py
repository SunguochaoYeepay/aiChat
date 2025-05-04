# -*- coding: utf-8 -*-
"""
模型包装器模块 - 提供统一的模型接口

此模块封装了模型加载和使用的功能，简化调用过程。
"""

import torch
import logging
import traceback
from transformers import AutoModelForCausalLM, AutoTokenizer

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
        """加载模型和分词器"""
        try:
            logger.info(f"开始加载模型: {self.model_path}")
            logger.info(f"设备: {self.device}, 精度: {self.precision}")
            logger.info(f"CUDA是否可用: {torch.cuda.is_available()}")
            
            if torch.cuda.is_available():
                logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB")
            
            # 加载tokenizer
            try:
                logger.info("加载tokenizer...")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path, 
                    trust_remote_code=True
                )
                logger.info("tokenizer加载成功")
            except Exception as e:
                logger.exception(f"tokenizer加载失败: {str(e)}")
                return False
            
            # 加载模型
            try:
                logger.info("加载model...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    trust_remote_code=True,
                    torch_dtype=self.torch_dtype,
                    low_cpu_mem_usage=True,
                    use_cache=True
                )
                logger.info("model加载成功")
            except Exception as e:
                logger.exception(f"model加载失败: {str(e)}")
                return False
            
            # 如果CUDA可用，将模型移至GPU
            if self.device == "cuda":
                try:
                    logger.info("将model移至CUDA...")
                    self.model = self.model.to(self.device)
                    logger.info("model已移至CUDA")
                except Exception as e:
                    logger.exception(f"将model移至CUDA失败: {str(e)}")
                    # 回退到CPU
                    logger.info("回退到CPU模式")
                    self.device = "cpu"
            
            # 设置为评估模式
            self.model = self.model.eval()
            
            # 标记模型已加载
            self.is_loaded = True
            logger.info("模型加载完成")
            
            # 验证模型
            try:
                logger.info("验证模型...")
                result, _ = self.model.chat(self.tokenizer, "测试", history=[])
                logger.info(f"模型验证成功，返回: {result[:50]}...")
            except Exception as e:
                logger.exception(f"模型验证失败: {str(e)}")
                # 尽管验证失败，但还是认为模型已加载
            
            return True
        except Exception as e:
            logger.exception(f"模型加载过程中遇到未处理的异常: {str(e)}")
            return False
    
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
