from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import torch
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, List, Dict, Any, Tuple
import os
import re
import uuid

# 字体设置
FONT_PATH = "SimSun.ttf"
FONT_SIZE = 15
try:
    FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    print(f"成功加载字体: {FONT_PATH}")
except Exception as e:
    print(f"无法加载字体 {FONT_PATH}: {e}")
    FONT = None

# 静态文件目录
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# 为边界框图像创建目录
BOX_IMAGE_DIR = os.path.join(STATIC_DIR, "box_images")
if not os.path.exists(BOX_IMAGE_DIR):
    os.makedirs(BOX_IMAGE_DIR)

app = FastAPI(title="本地Qwen-VL-Chat API 服务 (GPU加速版)")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 检查GPU可用性
if torch.cuda.is_available():
    print(f"检测到 GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU 显存: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB")
    device = "cuda"
else:
    print("警告: 未检测到GPU，将使用CPU运行（性能可能较低）")
    device = "cpu"

# 使用本地模型路径
model_id = "D:/AI-DEV/models/Qwen-VL-Chat-Int4"
print(f"正在加载本地模型 {model_id}...")

# 加载tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# 优化模型加载选项
model_load_start = time.time()
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",  # 自动选择最佳设备
    trust_remote_code=True,
    torch_dtype=torch.float16,  # GPU上使用半精度
    low_cpu_mem_usage=True,
    use_cache=True
).eval()

model_load_time = time.time() - model_load_start
print(f"模型加载完成! 耗时: {model_load_time:.2f}秒")
print(f"模型设备: {next(model.parameters()).device}")

# 知识库路径
KNOWLEDGE_BASE_PATH = "knowledge_base"

# 存储知识库内容
knowledge_base = {}

# 加载知识库
def load_knowledge_base():
    global knowledge_base
    knowledge_base = {}
    
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        os.makedirs(KNOWLEDGE_BASE_PATH)
        return {"status": "目录不存在，已创建空目录"}
    
    for filename in os.listdir(KNOWLEDGE_BASE_PATH):
        if filename.endswith(".md"):
            topic = filename.split(".")[0]
            file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            knowledge_base[topic] = content
    
    return {"status": "知识库加载成功", "topics": list(knowledge_base.keys())}

# 解析边界框的工具函数
def parse_boxes_from_text(text):
    """从文本中解析边界框信息"""
    print(f"解析文本中的边界框: {text}")
    
    # 匹配边界框格式: <box>(x1,y1),(x2,y2)</box>
    box_pattern = r"<box>\((\d+),(\d+)\),\((\d+),(\d+)\)</box>"
    # 匹配引用文本: <ref>文字</ref>
    ref_pattern = r"<ref>(.*?)</ref>"
    
    # 查找所有匹配项
    boxes = []
    refs = re.findall(ref_pattern, text)
    box_coords = re.findall(box_pattern, text)
    
    print(f"找到的refs: {refs}")
    print(f"找到的坐标: {box_coords}")
    
    # 坐标解析
    if len(box_coords) > 0:
        # 当匹配项数量不一致时，使用默认标签
        for i, coords in enumerate(box_coords):
            label = refs[i] if i < len(refs) else f"对象{i+1}"
            try:
                # 正确解析四个坐标值
                x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                print(f"解析坐标: {coords} -> ({x1}, {y1}, {x2}, {y2})")
                boxes.append((label, (x1, y1, x2, y2)))
            except Exception as e:
                print(f"解析坐标时出错: {e}")
    
    print(f"解析后的边界框: {boxes}")
    return boxes

# 在图像上绘制边界框
def draw_boxes_on_image(image, boxes):
    """在图像上绘制边界框"""
    draw = ImageDraw.Draw(image)
    
    print(f"开始绘制边界框，图像尺寸: {image.size}, 边界框: {boxes}")
    
    for label, (x1, y1, x2, y2) in boxes:
        # 模型返回的已经是像素坐标，无需缩放
        # 绘制方框
        draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)
        
        # 绘制标签背景
        text_width = len(label) * 9
        draw.rectangle([(x1, y1 - 20), (x1 + text_width, y1)], fill="red")
        
        # 绘制标签文字，使用加载的字体
        if FONT:
            draw.text((x1 + 5, y1 - 17), label, fill="white", font=FONT)
        else:
            draw.text((x1 + 5, y1 - 17), label, fill="white")
        print(f"已绘制边界框: {label} 在 ({x1}, {y1}, {x2}, {y2})")
    
    return image

# 保存带边界框的图像，并返回其URL
def save_boxed_image(image, boxes):
    """保存带边界框的图像，并返回其URL"""
    print(f"保存带边界框的图像，边界框: {boxes}")
    
    if not boxes:
        print("没有边界框，跳过保存图像")
        return None
        
    try:
        # 绘制边界框
        print(f"准备绘制边界框到图像上，图像类型: {type(image)}, 图像尺寸: {image.size}")
        boxed_image = draw_boxes_on_image(image.copy(), boxes)
        
        # 尝试保存到绝对路径
        try:
            absolute_path = "D:/AI-DEV/design-helper/debug_box_image.jpg"
            print(f"尝试保存到绝对路径: {absolute_path}")
            boxed_image.save(absolute_path)
            print(f"成功保存到绝对路径: {absolute_path}")
        except Exception as e:
            print(f"保存到绝对路径失败: {e}")
        
        # 确保目录存在并有写权限
        if not os.path.exists(BOX_IMAGE_DIR):
            try:
                print(f"创建边界框图像目录: {BOX_IMAGE_DIR}")
                os.makedirs(BOX_IMAGE_DIR, exist_ok=True)
                print(f"成功创建目录: {BOX_IMAGE_DIR}")
            except PermissionError as pe:
                print(f"创建目录权限错误: {pe}")
                return None
            except Exception as e:
                print(f"创建目录错误: {e}")
                return None
        
        # 检查目录写权限
        if not os.access(BOX_IMAGE_DIR, os.W_OK):
            print(f"警告: 目录 {BOX_IMAGE_DIR} 没有写入权限")
            try:
                # 尝试创建测试文件验证权限
                test_file = os.path.join(BOX_IMAGE_DIR, "test_write.txt")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print("权限测试通过")
            except Exception as e:
                print(f"权限测试失败: {e}")
                return None
        
        # 生成唯一文件名并保存
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(BOX_IMAGE_DIR, image_filename)
        
        print(f"保存边界框图像到路径: {image_path}")
        try:
            # 确保图像是正确的PIL Image对象
            if not isinstance(boxed_image, Image.Image):
                print(f"错误: boxed_image不是有效的PIL Image类型: {type(boxed_image)}")
                return None
                
            boxed_image.save(image_path)
            print(f"边界框图像已成功保存到: {image_path}")
            
            # 验证文件存在
            if os.path.exists(image_path):
                print(f"文件保存确认: {image_path} 存在，大小: {os.path.getsize(image_path)} 字节")
            else:
                print(f"警告: 文件保存失败，{image_path} 不存在")
                return None
        except Exception as e:
            print(f"保存图像文件错误: {e}")
            import traceback
            print(f"详细错误信息:\n{traceback.format_exc()}")
            return None
        
        # 返回URL
        url = f"/static/box_images/{image_filename}"
        print(f"生成的边界框图像URL: {url}")
        return url
    except Exception as e:
        import traceback
        print(f"保存边界框图像时出错: {str(e)}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
        return None

# 初始化加载知识库
load_knowledge_base()

class ChatRequest(BaseModel):
    messages: List[dict]

class ImageChatRequest(BaseModel):
    image_base64: str
    query: str

class KnowledgeRequest(BaseModel):
    topic: str
    query: str

@app.get("/")
async def root():
    """根路径"""
    return {"status": "服务运行中", "message": "本地Qwen-VL-Chat服务已启动", "device": device}

@app.get("/status")
async def status():
    """服务状态"""
    gpu_info = "不可用"
    if torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB",
            "memory_used": f"{torch.cuda.memory_allocated() / 1024 / 1024 / 1024:.2f} GB",
            "memory_reserved": f"{torch.cuda.memory_reserved() / 1024 / 1024 / 1024:.2f} GB"
        }
    
    return {
        "status": "运行中",
        "model_id": model_id,
        "device": str(next(model.parameters()).device),
        "gpu_info": gpu_info,
        "kb_topics": list(knowledge_base.keys())
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI 格式的聊天 API"""
    try:
        # 打印接收到的消息以便调试
        print(f"接收到的消息: {request.messages}")
        
        start_time = time.time()
        
        # 获取最后一条用户消息的内容
        user_query = request.messages[-1]["content"]
        
        # 构建历史消息
        history = None
        if len(request.messages) > 1:
            # 将之前的消息转换为模型需要的格式
            history = []
            for i in range(0, len(request.messages)-1, 2):
                if i+1 < len(request.messages):  # 确保有回复消息
                    user_msg = request.messages[i]["content"]
                    assistant_msg = request.messages[i+1]["content"]
                    history.append((user_msg, assistant_msg))
        
        # 确保使用GPU
        if torch.cuda.is_available():
            print(f"推理使用设备: {device} - 当前CUDA内存使用: {torch.cuda.memory_allocated() / 1024 / 1024 / 1024:.2f} GB")
            
        # 使用新的推荐语法
        with torch.amp.autocast(device_type='cuda', enabled=device=="cuda"):  # 在GPU上启用自动混合精度
            # 确认模型在GPU上
            first_param_device = next(model.parameters()).device
            print(f"模型实际设备: {first_param_device}")
            
            # 调用模型，强制走GPU
            response, _ = model.chat(
                tokenizer=tokenizer,
                query=user_query,
                history=history
            )
        
        process_time = time.time() - start_time
        print(f"处理时间: {process_time:.2f}秒")
        
        return {
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                }
            }],
            "processing_time": f"{process_time:.2f}秒"
        }
    except Exception as e:
        print(f"聊天错误详情: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_image(request: ImageChatRequest):
    """图片分析 API"""
    temp_img_path = "temp_image.jpg"
    try:
        # 解码 base64 图片
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 保存临时图像文件
        image.save(temp_img_path)
        print(f"临时图像已保存到: {temp_img_path}")
        
        # 构建查询 - 使用Qwen-VL官方格式
        query = request.query
        image_query = f"<img>{temp_img_path}</img>{query}"
        print(f"构建的图像查询: {image_query}")
        
        start_time = time.time()
        
        # 确保使用GPU
        if torch.cuda.is_available():
            print(f"图片分析推理使用设备: {device} - 当前CUDA内存使用: {torch.cuda.memory_allocated() / 1024 / 1024 / 1024:.2f} GB")
            
        # 确认模型在GPU上
        first_param_device = next(model.parameters()).device
        print(f"模型实际设备: {first_param_device}")
        
        # 使用标准的Qwen-VL图像处理方式
        print("开始调用模型进行图像分析...")
        with torch.amp.autocast(device_type='cuda', enabled=device=="cuda"):
            # 调用模型，使用标准的Qwen-VL格式
            response, _ = model.chat(
                tokenizer=tokenizer,
                query=image_query,
                history=None
            )
            print(f"模型响应: {response[:100]}...")
        
        process_time = time.time() - start_time
        print(f"图片分析处理时间: {process_time:.2f}秒")
        
        # 准备响应结果字典
        result = {
            "result": response,
            "processing_time": f"{process_time:.2f}秒"
        }
        
        # 检查响应是否包含边界框
        print("检查响应中的边界框...")
        boxes = parse_boxes_from_text(response)
        if boxes:
            print(f"检测到边界框: {boxes}")
            # 保存带边界框的图像
            try:
                image_copy = image.copy()  # 创建图像副本防止原图被修改
                boxed_image_url = save_boxed_image(image_copy, boxes)
                
                # 如果有边界框图像URL，添加到结果中
                if boxed_image_url:
                    print(f"添加边界框图像URL到结果: {boxed_image_url}")
                    result["boxed_image_url"] = boxed_image_url
                    # 添加完整的访问URL
                    result["boxed_image_full_url"] = f"http://localhost:8000{boxed_image_url}"
                else:
                    print("生成边界框图像失败，不添加URL")
            except Exception as e:
                import traceback
                print(f"处理边界框图像时出错: {str(e)}")
                print(f"详细错误信息:\n{traceback.format_exc()}")
                # 添加错误信息到结果中以便前端调试
                result["box_image_error"] = str(e)
        else:
            print("响应中没有检测到边界框")
        
        # 处理完成后删除临时文件
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            print("临时图像文件已删除")
            
        print(f"最终返回结果: {result}")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"图片分析错误: {error_msg}")
        
        # 输出更详细的错误信息
        import traceback
        traceback_str = traceback.format_exc()
        print(f"详细错误信息:\n{traceback_str}")
        
        # 确保发生错误时也删除临时文件
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            print("错误后临时图像文件已删除")
            
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/search")
async def search_knowledge_base(request: KnowledgeRequest):
    """知识库检索 API"""
    try:
        start_time = time.time()
        
        if request.topic not in knowledge_base:
            return {"result": f"未找到话题'{request.topic}'的相关内容"}
        
        # 获取话题内容
        content = knowledge_base[request.topic]
        
        # 构建模型提示
        prompt = f"""以下是关于"{request.topic}"的设计规范文档:
        
{content}

请根据上述设计规范，回答用户的问题: {request.query}
"""

        # 确保使用GPU
        if torch.cuda.is_available():
            print(f"知识库搜索推理使用设备: {device} - 当前CUDA内存使用: {torch.cuda.memory_allocated() / 1024 / 1024 / 1024:.2f} GB")
            
        # 使用新的推荐语法
        with torch.amp.autocast(device_type='cuda', enabled=device=="cuda"):  # 在GPU上启用自动混合精度
            # 确认模型在GPU上
            first_param_device = next(model.parameters()).device
            print(f"模型实际设备: {first_param_device}")
            
            # 调用模型
            response, _ = model.chat(
                tokenizer=tokenizer,
                query=prompt,
                history=None
            )
        
        process_time = time.time() - start_time
        print(f"知识库搜索处理时间: {process_time:.2f}秒")
        
        return {
            "result": response,
            "processing_time": f"{process_time:.2f}秒" 
        }
    except Exception as e:
        print(f"知识库搜索错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh_kb")
async def refresh_knowledge_base():
    """刷新知识库"""
    try:
        result = load_knowledge_base()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topics")
async def get_topics():
    """获取所有话题"""
    return {"topics": list(knowledge_base.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 