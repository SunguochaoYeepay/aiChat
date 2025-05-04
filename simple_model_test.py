import os
import sys
import torch

class SimpleModelTest:
    def run_tests(self):
        print("开始环境测试...")
        
        # 检查Python版本
        print(f"Python版本: {sys.version}")
        
        # 检查当前工作目录
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查CUDA可用性
        print(f"CUDA是否可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"GPU数量: {torch.cuda.device_count()}")
            print(f"当前GPU: {torch.cuda.current_device()}")
            print(f"GPU名称: {torch.cuda.get_device_name(0)}")
            print(f"CUDA版本: {torch.version.cuda}")
        
        # 检查PyTorch版本
        print(f"PyTorch版本: {torch.__version__}")
        
        try:
            # 检查Transformers
            import transformers
            print(f"Transformers版本: {transformers.__version__}")
            
            # 检查auto-gptq
            import auto_gptq
            print(f"auto-gptq版本: {auto_gptq.__version__}")
            
            # 检查Optimum（检查方式不同）
            import optimum
            print(f"Optimum已安装")
            
            # 检查Django
            import django
            print(f"Django版本: {django.__version__}")
            
            print("\n环境检查通过，所有必要的库都已安装!")
        except ImportError as e:
            print(f"\n环境检查失败: {str(e)}")
            
        # 尝试加载模型
        try:
            print("\n尝试加载模型...")
            from transformers import AutoTokenizer, AutoModelForCausalLM
            model_path = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
            
            print(f"模型路径是否存在: {os.path.exists(model_path)}")
            if not os.path.exists(model_path):
                print("模型路径不存在，无法继续测试")
                return
                
            print("加载tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            print("Tokenizer加载成功!")
            
            print("\n加载模型...")
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                use_cache=True
            )
            print("模型加载成功!")
            
            if torch.cuda.is_available():
                print("将模型移至GPU...")
                model = model.to("cuda")
                print("模型已移至GPU")
            
            # 检查模型的chat方法
            if hasattr(model, 'chat'):
                print("模型具有chat方法，尝试进行聊天...")
                response, history = model.chat(tokenizer, "你好，请介绍一下自己", history=[])
                print(f"模型响应: {response}")
            else:
                print("警告: 模型没有chat方法")
            
            print("\n环境测试完成!")
        except Exception as e:
            print(f"\n模型加载测试失败: {str(e)}")

if __name__ == "__main__":
    tester = SimpleModelTest()
    tester.run_tests() 