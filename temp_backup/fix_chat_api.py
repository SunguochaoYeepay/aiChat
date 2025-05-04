import os
import sys
import shutil
import subprocess
from pathlib import Path

# 运行命令并输出结果
def run_command(cmd, cwd=None):
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(f"输出:\n{result.stdout}")
    if result.stderr:
        print(f"错误:\n{result.stderr}")
    return result.returncode == 0

def main():
    # 获取当前目录
    current_dir = Path.cwd()
    
    # 准备安装所需的依赖项
    print("1. 确保Django项目的虚拟环境包含所有必需的依赖项")
    required_packages = [
        "torch torchvision --index-url https://download.pytorch.org/whl/cu121",
        "transformers optimum auto-gptq einops transformers_stream_generator matplotlib tiktoken"
    ]
    
    # 创建requirements_chat.txt文件
    requirements_file = current_dir / "requirements_chat.txt"
    with open(requirements_file, "w") as f:
        f.write("\n".join([
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "transformers>=4.30.0",
            "optimum>=1.16.0",
            "auto-gptq>=0.4.0",
            "einops>=0.6.0",
            "transformers_stream_generator>=0.0.4",
            "matplotlib>=3.7.0",
            "tiktoken>=0.4.0"
        ]))
    
    print(f"已创建依赖项文件: {requirements_file}")
    
    # 尝试创建一个包含特定模型函数调用的测试脚本
    test_script = current_dir / "test_model_wrapper.py"
    with open(test_script, "w") as f:
        f.write("""
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
""")
    
    print(f"已创建模型包装器测试脚本: {test_script}")
    print("运行测试脚本...")
    
    # 运行测试脚本
    run_command(f"{sys.executable} {test_script}")
    
    # 创建包装器模块
    wrapper_dir = current_dir / "admin_system" / "core" / "wrappers"
    wrapper_dir.mkdir(exist_ok=True)
    
    # 创建__init__.py文件
    init_file = wrapper_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("# 模型包装器模块\n")
    
    # 创建model_wrapper.py文件
    wrapper_file = wrapper_dir / "model_wrapper.py"
    with open(wrapper_file, "w") as f:
        f.write("""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelWrapper:
    \"\"\"
    模型包装器类 - 用于加载和使用量化模型
    
    此类提供了一个统一的接口来加载和使用各种模型，
    特别是针对需要特殊处理的量化模型（如GPTQ格式）。
    \"\"\"
    
    def __init__(self, model_path, device=None, precision="float16"):
        self.model_path = model_path
        self.device = device if device else "cuda" if torch.cuda.is_available() else "cpu"
        self.precision = precision
        self.torch_dtype = torch.float16 if precision == "float16" else torch.float32
        
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
    
    def load(self):
        \"\"\"加载模型和分词器\"\"\"
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
        \"\"\"
        进行对话
        
        Args:
            prompt: 用户输入的提示文本
            history: 对话历史记录
            
        Returns:
            tuple: (回复文本, 新的历史记录)
        \"\"\"
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
        \"\"\"
        简单的生成函数，不使用历史记录
        
        Args:
            prompt: 用户输入的提示文本
            
        Returns:
            str: 生成的响应文本
        \"\"\"
        return self.chat(prompt)[0]
""")
    
    print(f"已创建模型包装器模块: {wrapper_file}")
    
    # 更新model_service.py
    model_service_file = current_dir / "admin_system" / "core" / "model_service.py"
    if model_service_file.exists():
        # 备份原文件
        shutil.copy(model_service_file, str(model_service_file) + ".bak")
        print(f"已备份原始模型服务文件: {model_service_file}.bak")
        
        # 读取原文件内容
        with open(model_service_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 添加导入语句
        import_line = "from .wrappers.model_wrapper import ModelWrapper\n"
        if import_line not in content:
            import_section_end = content.find("# 全局变量")
            if import_section_end != -1:
                content = content[:import_section_end] + import_line + content[import_section_end:]
            else:
                content = import_line + content
        
        # 更新全局变量部分
        global_vars = """
# 全局变量
model = None
tokenizer = None
model_wrapper = None
model_load_time = None
model_config = None
"""
        content = content.replace("# 全局变量\nmodel = None\ntokenizer = None\nmodel_load_time = None\nmodel_config = None", global_vars)
        
        # 更新初始化模型函数
        init_model_func = """
def init_model(model_path=None, device=None, precision=None):
    \"\"\"
    初始化并加载模型
    
    Args:
        model_path: 模型路径
        device: 设备 ('cuda' 或 'cpu')
        precision: 精度 ('float16' 或 'float32')
    
    Returns:
        dict: 包含加载状态和时间的字典
    \"\"\"
    global model, tokenizer, model_wrapper, model_load_time, model_config
    
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
        
        # 创建模型包装器实例
        model_wrapper = ModelWrapper(model_path, device, precision)
        
        # 加载模型
        if model_wrapper.load():
            # 设置全局变量
            model = model_wrapper.model
            tokenizer = model_wrapper.tokenizer
            
            # 计算加载时间
            model_load_time = time.time() - load_start
            
            return {
                'status': 'success',
                'message': f'模型加载成功，耗时: {model_load_time:.2f}秒',
                'model_path': model_path,
                'device': device,
                'precision': precision
            }
        else:
            return {
                'status': 'error',
                'message': '模型加载失败，请查看日志获取详细信息'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'模型加载失败: {str(e)}'
        }
"""
        
        # 查找原函数并替换
        import re
        pattern = r"def init_model\([^)]*\):.*?Returns:.*?dict: .*?\n    \"\"\"\n.*?}\n"
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, init_model_func, content, flags=re.DOTALL)
        
        # 更新获取模型函数
        get_model_func = """
def get_model():
    \"\"\"
    获取模型实例
    
    Returns:
        tuple: (model, tokenizer) 元组
    \"\"\"
    global model, tokenizer, model_wrapper
    
    # 如果模型未加载，则加载模型
    if model is None or tokenizer is None:
        init_model()
    
    # 如果有模型包装器，则返回其模型和分词器
    if model_wrapper is not None:
        return model_wrapper.model, model_wrapper.tokenizer
        
    return model, tokenizer
"""
        
        # 查找原函数并替换
        pattern = r"def get_model\(\):.*?Returns:.*?tuple: .*?\n    \"\"\"\n.*?return model, tokenizer"
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, get_model_func, content, flags=re.DOTALL)
        
        # 写入更新后的内容
        with open(model_service_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"已更新模型服务文件: {model_service_file}")
    
    # 更新text_processing.py
    text_processing_file = current_dir / "admin_system" / "core" / "text_processing.py"
    if text_processing_file.exists():
        # 备份原文件
        shutil.copy(text_processing_file, str(text_processing_file) + ".bak")
        print(f"已备份原始文本处理文件: {text_processing_file}.bak")
        
        # 读取原文件内容
        with open(text_processing_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新chat_completion函数处理当前查询的部分
        updated_chat_completion = """
        # 流式响应处理
        if stream:
            # 这里使用生成器实现流式响应
            def generate_stream():
                try:
                    if model is None or not hasattr(model, 'chat'):
                        yield "模型未正确加载或不支持chat方法"
                        return
                    
                    response, _ = model.chat(tokenizer, prompt, history=history)
                    yield response
                except Exception as e:
                    yield f"生成流式响应时出错: {str(e)}"
                
            return {
                "stream": generate_stream(),
                "processing_time": "流式响应中"
            }
        else:
            # 标准响应
            try:
                if model is None:
                    return {
                        "error": "模型未加载",
                        "processing_time": "N/A"
                    }
                
                if not hasattr(model, 'chat'):
                    return {
                        "error": "模型不支持chat方法",
                        "processing_time": "N/A"
                    }
                
                response, new_history = model.chat(tokenizer, prompt, history=history)
"""
        
        # 替换相应部分
        start_marker = "        # 流式响应处理"
        end_marker = "                response, new_history = model.chat(tokenizer, prompt, history=history)"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + updated_chat_completion + content[end_idx:]
            
            # 写入更新后的内容
            with open(text_processing_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"已更新文本处理文件: {text_processing_file}")
    
    print("\n修复完成！请使用虚拟环境重启Django服务器，并再次测试聊天接口。")
    print("要启动服务器，请运行:")
    print(f"cd {current_dir / 'admin_system'} && python manage.py runserver")

if __name__ == "__main__":
    main() 