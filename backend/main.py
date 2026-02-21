from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

from .database import init_db, get_db, Conversation, Message
from .nl2sql_service import NL2SQLService
from .schemas import TABLES

# 初始化 NL2SQL 服务时进行错误检查
nl2sql_service = None
try:
    nl2sql_service = NL2SQLService()
    print("✅ NL2SQL 服务初始化成功")
except ValueError as e:
    print(f"\n{'='*60}")
    print(f"❌ NL2SQL 服务初始化失败\n")
    print(f"{str(e)}\n")
    print(f"{'='*60}\n")
    # 不退出，允许服务器启动但在调用 API 时返回错误
except Exception as e:
    print(f"\n{'='*60}")
    print(f"❌ 启动错误: {str(e)}\n")
    print(f"{'='*60}\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n✅ NL2SQL API 服务启动成功")
    print(f"📝 文档地址: http://localhost:8000/docs")
    print(f"❓ 健康检查: http://localhost:8000/health")
    print(f"{'='*60}\n")
    init_db()
    yield
    print("\n🛑 NL2SQL API 服务已关闭")


app = FastAPI(title="NL2SQL API", lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["content-type", "authorization"],
    expose_headers=["*"],
    max_age=3600,
)


@app.get("/")
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "message": "NL2SQL API is running"}


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    session_id: Optional[str] = Field(None, description="会话ID，可选")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "查询最近7天的病理报告",
                "session_id": "optional-session-id"
            }
        }


@app.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """处理聊天请求，生成 SQL 查询"""
    try:
        # 检查 NL2SQL 服务是否初始化成功
        if nl2sql_service is None:
            raise HTTPException(
                status_code=503,
                detail="❌ NL2SQL 服务未初始化，请检查 API 密钥配置\n请查看 API_KEY_SETUP.md 获取帮助"
            )
        
        # 验证输入
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")

        session_id = request.session_id or str(uuid.uuid4())

        conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not conv:
            conv = Conversation(
                session_id=session_id,
                title=request.question[:50],
                created_at=datetime.now(tz=timezone.utc),
                updated_at=datetime.now(tz=timezone.utc)
            )
            db.add(conv)
            db.commit()

        messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
        history = [{"role": m.role, "content": m.content} for m in messages]

        user_msg = Message(
            session_id=session_id,
            role="user",
            content=request.question,
            created_at=datetime.now(tz=timezone.utc)
        )
        db.add(user_msg)
        db.commit()

        result = await nl2sql_service.process_question(request.question, history)

        assistant_content = f"```sql\n{result['sql']}\n```\n\n{result['explanation']}"
        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            sql_result=json.dumps(result),
            created_at=datetime.now(tz=timezone.utc)
        )
        db.add(assistant_msg)

        conv.updated_at = datetime.now(tz=timezone.utc)
        db.commit()

        return {**result, "session_id": session_id}
    
    except HTTPException:
        raise
    except ValueError as e:
        # API 密钥配置错误
        print(f"❌ Configuration error: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error in chat endpoint: {error_str}")
        
        # 检测认证错误
        if "401" in error_str or "AuthenticationError" in error_str or "Unauthorized" in error_str:
            provider = os.getenv("LLM_PROVIDER", "ark").strip().lower()
            api_key_name = "SILICONFLOW_API_KEY" if provider == "siliconflow" else "ARK_API_KEY"
            provider_console = "https://cloud.siliconflow.cn/" if provider == "siliconflow" else "https://console.volcengine.com/"
            detail = (
                "❌ API 认证失败\n\n"
                "请检查：\n"
                f"1. backend/.env 中的 {api_key_name} 是否正确\n"
                "2. API 密钥是否已过期\n"
                "3. API 密钥是否有效且有权限\n\n"
                "获取新密钥：\n"
                f"访问 {provider_console} 并重新配置 API 密钥"
            )
            raise HTTPException(status_code=401, detail=detail)
        
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {error_str}")


@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):
    convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    return [
        {
            "session_id": c.session_id,
            "title": c.title,
            "created_at": str(c.created_at),
            "updated_at": str(c.updated_at)
        }
        for c in convs
    ]


@app.get("/api/history/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
    result = []
    for m in messages:
        msg_dict = {"id": m.id, "role": m.role, "content": m.content, "created_at": str(m.created_at)}
        if m.sql_result:
            msg_dict["sql_data"] = json.loads(m.sql_result)
        result.append(msg_dict)
    return result


@app.get("/api/tables")
async def get_tables():
    return TABLES


@app.delete("/api/history/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.query(Conversation).filter(Conversation.session_id == session_id).delete()
    db.commit()
    return {"status": "deleted"}
