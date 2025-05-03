from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import base64
import os
import sys

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

# 主页路由
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

class AnalyzeRequest(BaseModel):
    topic: str
    image_base64: str
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 