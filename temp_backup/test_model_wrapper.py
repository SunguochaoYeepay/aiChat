
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
        print("���ڼ���ģ��...")
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
        
        # ���CUDA���ã���ģ������GPU
        if torch.cuda.is_available():
            print("��ģ������GPU...")
            self.model = self.model.to("cuda")
        
        # ����Ϊ����ģʽ
        self.model = self.model.eval()
        print("ģ�ͼ������")
    
    def chat(self, prompt, history=None):
        # ȷ��ģ���Ѽ���
        if self.model is None or self.tokenizer is None:
            self.load()
        
        if history is None:
            history = []
        
        # ����ģ�͵�chat����
        response, new_history = self.model.chat(self.tokenizer, prompt, history=history)
        return response, new_history
    
    def generate(self, prompt):
        # �򵥵����ɺ�������ʹ����ʷ��¼
        return self.chat(prompt)[0]

# ����ModelWrapper
if __name__ == "__main__":
    model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
    wrapper = ModelWrapper(model_path)
    
    # ���Լ���
    wrapper.load()
    
    # ���ԶԻ�
    prompt = "��ã������һ���Լ�"
    response, _ = wrapper.chat(prompt)
    print(f"����: {prompt}")
    print(f"�ش�: {response}")
