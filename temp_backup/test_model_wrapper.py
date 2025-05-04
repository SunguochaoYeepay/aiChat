
import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelWrapper:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
    
    def load(self):
        print("正在加载模型...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, 
            trust_remote_code=True
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            use_cache=True
        )
        
        # 如果CUDA可用，将模型移至GPU
        if torch.cuda.is_available():
            print("将模型移至GPU...")
            self.model = self.model.to("cuda")
        
        # 设置为评估模式
        self.model = self.model.eval()
        print("模型加载完成")
    
    def chat(self, prompt, history=None):
        # 确保模型已加载
        if self.model is None or self.tokenizer is None:
            self.load()
        
        if history is None:
            history = []
        
        # 调用模型的chat方法
        response, new_history = self.model.chat(self.tokenizer, prompt, history=history)
        return response, new_history
    
    def generate(self, prompt):
        # 简单的生成函数，不使用历史记录
        return self.chat(prompt)[0]

# 测试ModelWrapper
if __name__ == "__main__":
    model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
    wrapper = ModelWrapper(model_path)
    
    # 测试加载
    wrapper.load()
    
    # 测试对话
    prompt = "你好，请介绍一下自己"
    response, _ = wrapper.chat(prompt)
    print(f"提问: {prompt}")
    print(f"回答: {response}")
