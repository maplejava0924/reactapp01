# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# CORS フロントエンドとバックエンド間の通信を許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # テスト用に5秒待機
    time.sleep(5)
    # 仮の返信（のちにLangChain処理に置き換える）
    return ChatResponse(reply=f"（FastAPIの返答）あなたはこう言いましたね：{req.message}")
