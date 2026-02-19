from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

from database import init_db, get_db, Conversation, Message
from nl2sql_service import NL2SQLService
from schemas import TABLES

app = FastAPI(title="NL2SQL API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nl2sql_service = NL2SQLService()


@app.on_event("startup")
async def startup():
    init_db()


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


@app.post("/api/chat")
async def chat(request: ChatRequest):
    db = next(get_db())
    try:
        session_id = request.session_id or str(uuid.uuid4())

        conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not conv:
            conv = Conversation(
                session_id=session_id,
                title=request.question[:50],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(conv)
            db.commit()

        messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
        history = [{"role": m.role, "content": m.content} for m in messages]

        user_msg = Message(
            session_id=session_id,
            role="user",
            content=request.question,
            created_at=datetime.utcnow()
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
            created_at=datetime.utcnow()
        )
        db.add(assistant_msg)

        conv.updated_at = datetime.utcnow()
        db.commit()

        return {**result, "session_id": session_id}
    finally:
        db.close()


@app.get("/api/history")
async def get_history():
    db = next(get_db())
    try:
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
    finally:
        db.close()


@app.get("/api/history/{session_id}")
async def get_session(session_id: str):
    db = next(get_db())
    try:
        messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
        result = []
        for m in messages:
            msg_dict = {"id": m.id, "role": m.role, "content": m.content, "created_at": str(m.created_at)}
            if m.sql_result:
                msg_dict["sql_data"] = json.loads(m.sql_result)
            result.append(msg_dict)
        return result
    finally:
        db.close()


@app.get("/api/tables")
async def get_tables():
    return TABLES


@app.delete("/api/history/{session_id}")
async def delete_session(session_id: str):
    db = next(get_db())
    try:
        db.query(Message).filter(Message.session_id == session_id).delete()
        db.query(Conversation).filter(Conversation.session_id == session_id).delete()
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()
