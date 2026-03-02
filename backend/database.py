from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///./nl2sql.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    title = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    sql_result = Column(Text, nullable=True)
    created_at = Column(DateTime)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)

class DatabaseVendor(Base):
    __tablename__ = "database_vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    display_name = Column(String)

class SchemaLibrary(Base):
    __tablename__ = "schema_libraries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    tables = relationship("SchemaTable", back_populates="library", cascade="all, delete-orphan")

class SchemaTable(Base):
    __tablename__ = "schema_tables"
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("schema_libraries.id", ondelete="CASCADE"))
    table_name = Column(String)
    description = Column(String, nullable=True)
    library = relationship("SchemaLibrary", back_populates="tables")
    fields = relationship("SchemaField", back_populates="table", cascade="all, delete-orphan")

class SchemaField(Base):
    __tablename__ = "schema_fields"
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("schema_tables.id", ondelete="CASCADE"))
    name = Column(String)
    field_type = Column(String)
    description = Column(String, nullable=True)
    table = relationship("SchemaTable", back_populates="fields")

class TableRelation(Base):
    __tablename__ = "table_relations"
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("schema_libraries.id", ondelete="CASCADE"))
    from_table = Column(String)
    from_column = Column(String)
    to_table = Column(String)
    to_column = Column(String)
    description = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
