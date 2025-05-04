# -*- coding: utf-8 -*-
"""
模型包装器模块 - 提供统一的模型接口

此模块封装了模型加载和使用的功能，简化调用过程。
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

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
    
    def load(self):
        """加载模型和分词器"""
        try:
            print(f"正在加载模型: {self.model_path}")
            print(f"设备: {self.device}, 精度: {self.precision}")
            
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_cache=True
            )
            
            # 如果CUDA可用，将模型移至GPU
            if self.device == "cuda":
                self.model = self.model.to(self.device)
            
            # 设置为评估模式
            self.model = self.model.eval()
            
            # 标记模型已加载
            self.is_loaded = True
            print("模型加载完成")
            
            return True
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
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
            self.load()
        
        if history is None:
            history = []
        
        try:
            # 调用模型的chat方法
            response, new_history = self.model.chat(self.tokenizer, prompt, history=history)
            return response, new_history
        except Exception as e:
            print(f"聊天生成出错: {str(e)}")
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
