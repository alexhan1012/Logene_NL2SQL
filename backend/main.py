from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

from .database import (
    init_db, get_db, Conversation, Message,
    Setting, DatabaseVendor, SchemaLibrary, SchemaTable, SchemaField
)
from .nl2sql_service import NL2SQLService
from .schemas import TABLES

# 初始化 NL2SQL 服务时进行错误检查
nl2sql_service = None
try:
    nl2sql_service = NL2SQLService()
    print("[OK] NL2SQL 服务初始化成功")
except ValueError as e:
    print(f"\n{'='*60}")
    print(f"[ERROR] NL2SQL 服务初始化失败\n")
    print(f"{str(e)}\n")
    print(f"{'='*60}\n")
    # 不退出，允许服务器启动但在调用 API 时返回错误
except Exception as e:
    print(f"\n{'='*60}")
    print(f"[ERROR] 启动错误: {str(e)}\n")
    print(f"{'='*60}\n")


def _seed_defaults(db: Session):
    """Seed default database vendors and a default schema library if empty."""
    if db.query(DatabaseVendor).count() == 0:
        defaults = [
            ("sqlserver", "SQL Server"),
            ("oracle", "Oracle"),
            ("postgresql", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("kingbasees", "人大金仓"),
            ("dm", "达梦"),
        ]
        for name, display in defaults:
            db.add(DatabaseVendor(name=name, display_name=display))
        db.commit()

    if db.query(SchemaLibrary).count() == 0:
        lib = SchemaLibrary(name="默认病理库", description="默认的病理信息系统数据库表结构")
        db.add(lib)
        db.commit()
        db.refresh(lib)
        for table_name, table_info in TABLES.items():
            st = SchemaTable(library_id=lib.id, table_name=table_name, description=table_info["description"])
            db.add(st)
            db.commit()
            db.refresh(st)
            for field in table_info["fields"]:
                db.add(SchemaField(
                    table_id=st.id,
                    name=field["name"],
                    field_type=field["type"],
                    description=field["description"]
                ))
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n[OK] NL2SQL API 服务启动成功")
    print(f"[INFO] 文档地址: http://localhost:8000/docs")
    print(f"[INFO] 健康检查: http://localhost:8000/health")
    print(f"{'='*60}\n")
    init_db()
    db = next(get_db())
    try:
        _seed_defaults(db)
    finally:
        db.close()
    yield
    print("\n[INFO] NL2SQL API 服务已关闭")


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


# ─── Helper: build tables_dict from a SchemaLibrary ───

def _library_to_tables_dict(db: Session, library_id: int) -> dict:
    tables = db.query(SchemaTable).filter(SchemaTable.library_id == library_id).all()
    result = {}
    for t in tables:
        fields = db.query(SchemaField).filter(SchemaField.table_id == t.id).all()
        result[t.table_name] = {
            "description": t.description or "",
            "fields": [{"name": f.name, "type": f.field_type, "description": f.description or ""} for f in fields]
        }
    return result


# ─── Chat ───

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    session_id: Optional[str] = Field(None, description="会话ID，可选")
    db_vendor: Optional[str] = Field(None, description="数据库厂商")
    schema_library_id: Optional[int] = Field(None, description="Schema库ID")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "查询最近7天的病理报告",
                "session_id": "optional-session-id",
                "db_vendor": "sqlserver",
                "schema_library_id": 1
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

        # Resolve tables dict
        tables_dict = None
        if request.schema_library_id:
            tables_dict = _library_to_tables_dict(db, request.schema_library_id) or None

        result = await nl2sql_service.process_question(
            request.question, history,
            tables_dict=tables_dict,
            db_vendor=request.db_vendor
        )

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
        print(f"[ERROR] Configuration error: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        error_str = str(e)
        print(f"[ERROR] Error in chat endpoint: {error_str}")
        
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


# ─── History ───

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
async def get_tables(library_id: Optional[int] = None, db: Session = Depends(get_db)):
    if library_id:
        tables_dict = _library_to_tables_dict(db, library_id)
        if tables_dict:
            return tables_dict
    return TABLES


@app.delete("/api/history/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.query(Conversation).filter(Conversation.session_id == session_id).delete()
    db.commit()
    return {"status": "deleted"}


# ─── Settings ───

class SettingUpdate(BaseModel):
    key: str
    value: str

@app.get("/api/settings")
async def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}

@app.put("/api/settings")
async def update_settings(items: List[SettingUpdate], db: Session = Depends(get_db)):
    for item in items:
        existing = db.query(Setting).filter(Setting.key == item.key).first()
        if existing:
            existing.value = item.value
        else:
            db.add(Setting(key=item.key, value=item.value))
    db.commit()
    return {"status": "ok"}


# ─── Database Vendors ───

class VendorCreate(BaseModel):
    name: str
    display_name: str

@app.get("/api/vendors")
async def list_vendors(db: Session = Depends(get_db)):
    vendors = db.query(DatabaseVendor).all()
    return [{"id": v.id, "name": v.name, "display_name": v.display_name} for v in vendors]

@app.post("/api/vendors")
async def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    existing = db.query(DatabaseVendor).filter(DatabaseVendor.name == vendor.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="该数据库厂商已存在")
    v = DatabaseVendor(name=vendor.name, display_name=vendor.display_name)
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"id": v.id, "name": v.name, "display_name": v.display_name}

@app.delete("/api/vendors/{vendor_id}")
async def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db.query(DatabaseVendor).filter(DatabaseVendor.id == vendor_id).delete()
    db.commit()
    return {"status": "deleted"}


# ─── Schema Libraries ───

class LibraryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class LibraryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

@app.get("/api/schema-libraries")
async def list_libraries(db: Session = Depends(get_db)):
    libs = db.query(SchemaLibrary).all()
    return [{"id": l.id, "name": l.name, "description": l.description} for l in libs]

@app.post("/api/schema-libraries")
async def create_library(lib: LibraryCreate, db: Session = Depends(get_db)):
    l = SchemaLibrary(name=lib.name, description=lib.description)
    db.add(l)
    db.commit()
    db.refresh(l)
    return {"id": l.id, "name": l.name, "description": l.description}

@app.put("/api/schema-libraries/{library_id}")
async def update_library(library_id: int, lib: LibraryUpdate, db: Session = Depends(get_db)):
    existing = db.query(SchemaLibrary).filter(SchemaLibrary.id == library_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="库不存在")
    if lib.name is not None:
        existing.name = lib.name
    if lib.description is not None:
        existing.description = lib.description
    db.commit()
    return {"id": existing.id, "name": existing.name, "description": existing.description}

@app.delete("/api/schema-libraries/{library_id}")
async def delete_library(library_id: int, db: Session = Depends(get_db)):
    db.query(SchemaLibrary).filter(SchemaLibrary.id == library_id).delete()
    db.commit()
    return {"status": "deleted"}


# ─── Schema Tables ───

class TableCreate(BaseModel):
    table_name: str
    description: Optional[str] = None

class TableUpdate(BaseModel):
    table_name: Optional[str] = None
    description: Optional[str] = None

@app.get("/api/schema-libraries/{library_id}/tables")
async def list_library_tables(library_id: int, db: Session = Depends(get_db)):
    tables = db.query(SchemaTable).filter(SchemaTable.library_id == library_id).all()
    result = []
    for t in tables:
        fields = db.query(SchemaField).filter(SchemaField.table_id == t.id).all()
        result.append({
            "id": t.id,
            "table_name": t.table_name,
            "description": t.description,
            "fields": [{"id": f.id, "name": f.name, "type": f.field_type, "description": f.description} for f in fields]
        })
    return result

@app.post("/api/schema-libraries/{library_id}/tables")
async def create_table(library_id: int, table: TableCreate, db: Session = Depends(get_db)):
    t = SchemaTable(library_id=library_id, table_name=table.table_name, description=table.description)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "table_name": t.table_name, "description": t.description, "fields": []}

@app.put("/api/schema-tables/{table_id}")
async def update_table(table_id: int, table: TableUpdate, db: Session = Depends(get_db)):
    t = db.query(SchemaTable).filter(SchemaTable.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="表不存在")
    if table.table_name is not None:
        t.table_name = table.table_name
    if table.description is not None:
        t.description = table.description
    db.commit()
    return {"id": t.id, "table_name": t.table_name, "description": t.description}

@app.delete("/api/schema-tables/{table_id}")
async def delete_table(table_id: int, db: Session = Depends(get_db)):
    db.query(SchemaTable).filter(SchemaTable.id == table_id).delete()
    db.commit()
    return {"status": "deleted"}


# ─── Schema Fields ───

class FieldCreate(BaseModel):
    name: str
    field_type: str
    description: Optional[str] = None

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    field_type: Optional[str] = None
    description: Optional[str] = None

@app.post("/api/schema-tables/{table_id}/fields")
async def create_field(table_id: int, field: FieldCreate, db: Session = Depends(get_db)):
    f = SchemaField(table_id=table_id, name=field.name, field_type=field.field_type, description=field.description)
    db.add(f)
    db.commit()
    db.refresh(f)
    return {"id": f.id, "name": f.name, "type": f.field_type, "description": f.description}

@app.put("/api/schema-fields/{field_id}")
async def update_field(field_id: int, field: FieldUpdate, db: Session = Depends(get_db)):
    f = db.query(SchemaField).filter(SchemaField.id == field_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="字段不存在")
    if field.name is not None:
        f.name = field.name
    if field.field_type is not None:
        f.field_type = field.field_type
    if field.description is not None:
        f.description = field.description
    db.commit()
    return {"id": f.id, "name": f.name, "type": f.field_type, "description": f.description}

@app.delete("/api/schema-fields/{field_id}")
async def delete_field(field_id: int, db: Session = Depends(get_db)):
    db.query(SchemaField).filter(SchemaField.id == field_id).delete()
    db.commit()
    return {"status": "deleted"}
