from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from backend.app.database.session import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, default="default")
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)  # JSON string of tool calls
    created_at = Column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), index=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    remind_at = Column(String(100), nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
