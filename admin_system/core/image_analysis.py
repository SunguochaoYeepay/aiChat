"""
图像分析模块 - 负责图像处理和分析功能

此模块提供图像分析、目标检测、边界框处理等功能，是从FastAPI服务迁移的核心功能。
"""
import os
import re
import json
import uuid
import time
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from pathlib import Path

from .model_service import get_model

# 字体设置
FONT_PATH = "SimSun.ttf"
FONT_SIZE = 15
try:
    FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    print(f"成功加载字体: {FONT_PATH}")
except Exception as e:
    print(f"无法加载字体 {FONT_PATH}: {e}")
    FONT = None

def get_box_image_dir():
    """获取边界框图像存储目录"""
    from django.conf import settings
    
    # 静态文件目录
    static_dir = os.path.join(settings.BASE_DIR, 'static')
    box_image_dir = os.path.join(static_dir, 'box_images')
    
    # 确保目录存在
    os.makedirs(box_image_dir, exist_ok=True)
    
    return box_image_dir

def parse_base64_image(image_base64):
    """解析Base64编码的图像"""
    if isinstance(image_base64, list):
        # 处理图像列表
        images = []
        for img_str in image_base64:
            if ',' in img_str:
                # 处理 "data:image/jpeg;base64,/9j/4AAQ..." 格式
                img_str = img_str.split(',', 1)[1]
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))
            images.append(img)
        return images
    else:
        # 处理单张图像
        if ',' in image_base64:
            # 处理 "data:image/jpeg;base64,/9j/4AAQ..." 格式
            image_base64 = image_base64.split(',', 1)[1]
        img_data = base64.b64decode(image_base64)
        return Image.open(BytesIO(img_data))

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

def save_boxed_image(image, boxes):
    """保存带边界框的图像，并返回其URL"""
    print(f"保存带边界框的图像，边界框: {boxes}")
    
    if not boxes:
        print("没有边界框，跳过保存图像")
        return None
        
    try:
        # 如果图像是RGBA模式，转换为RGB模式
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        # 绘制边界框
        print(f"准备绘制边界框到图像上，图像类型: {type(image)}, 图像尺寸: {image.size}")
        boxed_image = draw_boxes_on_image(image.copy(), boxes)
        
        # 生成唯一文件名
        filename = f"box_{uuid.uuid4().hex}.jpg"
        box_image_dir = get_box_image_dir()
        file_path = os.path.join(box_image_dir, filename)
        
        # 保存图像
        boxed_image.save(file_path, format="JPEG")
        print(f"边界框图像已保存到 {file_path}")
        
        # 返回相对URL
        rel_url = f"/static/box_images/{filename}"
        print(f"边界框图像URL: {rel_url}")
        return rel_url
        
    except Exception as e:
        print(f"保存边界框图像时出错: {e}")
        return None

def analyze_image(image_base64, query):
    """
    分析图像并回答问题
    
    Args:
        image_base64: Base64编码的图像或图像列表
        query: 用户查询
    
    Returns:
        dict: 包含分析结果和处理时间的字典
    """
    try:
        # 获取开始时间
        start_time = time.time()
        
        # 解析图像
        images = parse_base64_image(image_base64)
        if not isinstance(images, list):
            images = [images]
        
        # 获取模型和tokenizer
        model, tokenizer = get_model()
        
        # 检查模型和tokenizer是否成功加载
        if model is None or tokenizer is None:
            error_msg = "模型或tokenizer加载失败，无法进行图像分析"
            print(f"错误: {error_msg}")
            return {
                "result": f"分析过程中出错: {error_msg}",
                "processing_time": "N/A",
                "error": error_msg
            }
        
        # 处理多张图片的情况
        if len(images) > 1:
            # 多张图片分析
            results = []
            boxed_image_urls = []
            
            for i, image in enumerate(images):
                # 临时保存图像以获取图像路径
                temp_img_path = f"temp_image_{i}_{uuid.uuid4().hex}.jpg"
                image_dir = os.path.join(settings.BASE_DIR, 'static', 'temp_images')
                os.makedirs(image_dir, exist_ok=True)
                full_img_path = os.path.join(image_dir, temp_img_path)
                
                # 保存图像
                image.save(full_img_path, format="JPEG")
                print(f"临时图像已保存到: {full_img_path}")
                
                # 构建提示词
                img_query = f"图片{i+1}: {query}" if len(images) > 1 else query
                
                # 使用from_list_format方法构建输入
                model_inputs = tokenizer.from_list_format([
                    {'image': full_img_path},
                    {'text': img_query}
                ])
                
                # 调用模型 - 不再直接传递image参数
                response, history = model.chat(
                    tokenizer,
                    model_inputs,
                    history=[]
                )
                
                # 解析边界框
                boxes = parse_boxes_from_text(response)
                
                # 保存带边界框的图像
                boxed_url = save_boxed_image(image, boxes) if boxes else None
                
                # 收集结果
                results.append(response)
                if boxed_url:
                    boxed_image_urls.append(boxed_url)
                
                # 删除临时图像
                try:
                    os.remove(full_img_path)
                    print(f"临时图像已删除: {full_img_path}")
                except Exception as e:
                    print(f"删除临时图像时出错: {e}")
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            return {
                "result": results,
                "processing_time": f"{processing_time:.2f}秒",
                "boxed_image_urls": boxed_image_urls if boxed_image_urls else None
            }
        else:
            # 单张图片分析
            image = images[0]
            
            # 临时保存图像以获取图像路径
            temp_img_path = f"temp_image_{uuid.uuid4().hex}.jpg"
            image_dir = os.path.join(settings.BASE_DIR, 'static', 'temp_images')
            os.makedirs(image_dir, exist_ok=True)
            full_img_path = os.path.join(image_dir, temp_img_path)
            
            # 保存图像
            image.save(full_img_path, format="JPEG")
            print(f"临时图像已保存到: {full_img_path}")
            
            # 使用from_list_format方法构建输入
            model_inputs = tokenizer.from_list_format([
                {'image': full_img_path},
                {'text': query}
            ])
            
            # 调用模型 - 不再直接传递image参数
            response, history = model.chat(
                tokenizer,
                model_inputs,
                history=[]
            )
            
            # 解析边界框
            boxes = parse_boxes_from_text(response)
            
            # 保存带边界框的图像
            boxed_url = save_boxed_image(image, boxes) if boxes else None
            
            # 删除临时图像
            try:
                os.remove(full_img_path)
                print(f"临时图像已删除: {full_img_path}")
            except Exception as e:
                print(f"删除临时图像时出错: {e}")
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            return {
                "result": response,
                "processing_time": f"{processing_time:.2f}秒",
                "boxed_image_url": boxed_url
            }
            
    except Exception as e:
        return {
            "result": f"分析过程中出错: {str(e)}",
            "processing_time": "N/A",
            "error": str(e)
        } 