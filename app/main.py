from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import base64
import os
import sys
import json
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.kb_retriever import KnowledgeBase
from app.llm_api import QwenAPI
from app.config import HOST, PORT

app = FastAPI(title="设计助手后端服务")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
kb = KnowledgeBase()
qwen_api = QwenAPI()

# 静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

# 初始化连接管理器
manager = ConnectionManager()

# 主页路由
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

class AnalyzeRequest(BaseModel):
    topic: str
    image_base64: Union[str, List[str]]  # 支持单张图片或图片列表
    question: str

class SearchRequest(BaseModel):
    topic: str
    question: str

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """分析图片并回答问题"""
    try:
        # 从知识库获取相关信息
        kb_content = kb.search(request.topic, request.question)
        
        # 调用 Qwen-VL-Chat 分析图片
        analysis = qwen_api.analyze_image(
            request.topic,
            request.image_base64,
            f"{request.question}\n\n相关设计规范：\n{kb_content}"
        )
        
        return {"result": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(request: SearchRequest):
    """搜索知识库"""
    try:
        result = kb.search(request.topic, request.question)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh_kb")
async def refresh_kb():
    """刷新知识库"""
    try:
        result = kb.refresh()
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket路由：图像分析
@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 接收数据
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # 验证请求字段
            if not all(k in request_data for k in ["topic", "image_base64", "question"]):
                await manager.send_json(websocket, {
                    "status": "error", 
                    "message": "请求格式错误，缺少必要字段"
                })
                continue
            
            # 图片可以是单张或多张
            if not isinstance(request_data["image_base64"], (str, list)):
                await manager.send_json(websocket, {
                    "status": "error", 
                    "message": "image_base64必须是字符串或字符串列表"
                })
                continue
                
            # 如果是列表，检查是否为空或包含非字符串元素
            if isinstance(request_data["image_base64"], list):
                if not request_data["image_base64"]:
                    await manager.send_json(websocket, {
                        "status": "error", 
                        "message": "image_base64列表不能为空"
                    })
                    continue
                
                if not all(isinstance(img, str) for img in request_data["image_base64"]):
                    await manager.send_json(websocket, {
                        "status": "error", 
                        "message": "image_base64列表中必须全为字符串"
                    })
                    continue
            
            # 发送处理状态
            await manager.send_json(websocket, {
                "status": "processing", 
                "message": "正在从知识库获取相关信息..."
            })
            
            try:
                # 从知识库获取相关信息
                kb_content = kb.search(request_data["topic"], request_data["question"])
                
                await manager.send_json(websocket, {
                    "status": "processing", 
                    "message": "正在分析图像..."
                })
                
                # 调用 Qwen-VL-Chat 分析图片
                analysis = qwen_api.analyze_image(
                    request_data["topic"],
                    request_data["image_base64"],
                    f"{request_data['question']}\n\n相关设计规范：\n{kb_content}"
                )
                
                # 发送结果
                await manager.send_json(websocket, {
                    "status": "complete",
                    "result": analysis,
                    # 如果API返回的分析结果是字典且包含边界框图像URLs，则一并返回
                    "boxed_image_urls": analysis.get("boxed_image_urls") if isinstance(analysis, dict) and "boxed_image_urls" in analysis else None,
                    "boxed_image_url": analysis.get("boxed_image_url") if isinstance(analysis, dict) and "boxed_image_url" in analysis else None
                })
                
            except Exception as e:
                await manager.send_json(websocket, {
                    "status": "error",
                    "message": f"处理失败: {str(e)}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        try:
            await manager.send_json(websocket, {
                "status": "error",
                "message": f"连接错误: {str(e)}"
            })
        except:
            pass
        manager.disconnect(websocket)

# WebSocket路由：知识库搜索
@app.websocket("/ws/search")
async def websocket_search(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 接收数据
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # 验证请求字段
            if not all(k in request_data for k in ["topic", "question"]):
                await manager.send_json(websocket, {
                    "status": "error", 
                    "message": "请求格式错误，缺少必要字段"
                })
                continue
            
            # 发送处理状态
            await manager.send_json(websocket, {
                "status": "processing", 
                "message": "正在搜索知识库..."
            })
            
            try:
                # 搜索知识库
                result = kb.search(request_data["topic"], request_data["question"])
                
                # 发送结果
                await manager.send_json(websocket, {
                    "status": "complete",
                    "result": result
                })
                
            except Exception as e:
                await manager.send_json(websocket, {
                    "status": "error",
                    "message": f"搜索失败: {str(e)}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        try:
            await manager.send_json(websocket, {
                "status": "error",
                "message": f"连接错误: {str(e)}"
            })
        except:
            pass
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 