from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.crud import (
    save_memory, get_all_memories, create_note, get_notes,
    create_reminder, get_pending_reminders, get_conversation_history
)

router = APIRouter(prefix="/api/memory", tags=["Memory & Persistence"])

class MemoryRequest(BaseModel):
    key: str
    value: str
    category: str = "preference"

class NoteRequest(BaseModel):
    title: str
    content: str

class ReminderRequest(BaseModel):
    title: str
    remind_at: str

@router.get("/memories")
def get_memories_endpoint(db: Session = Depends(get_db)):
    mems = get_all_memories(db)
    return [{"id": m.id, "key": m.key, "value": m.value, "category": m.category} for m in mems]

@router.post("/memories")
def add_memory_endpoint(req: MemoryRequest, db: Session = Depends(get_db)):
    mem = save_memory(db, key=req.key, value=req.value, category=req.category)
    return {"success": True, "id": mem.id, "key": mem.key, "value": mem.value}

@router.get("/notes")
def get_notes_endpoint(db: Session = Depends(get_db)):
    notes = get_notes(db)
    return [{"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at.isoformat()} for n in notes]

@router.post("/notes")
def create_note_endpoint(req: NoteRequest, db: Session = Depends(get_db)):
    n = create_note(db, title=req.title, content=req.content)
    return {"success": True, "id": n.id, "title": n.title}

@router.get("/reminders")
def get_reminders_endpoint(db: Session = Depends(get_db)):
    reminders = get_pending_reminders(db)
    return [{"id": r.id, "title": r.title, "remind_at": r.remind_at} for r in reminders]

@router.post("/reminders")
def create_reminder_endpoint(req: ReminderRequest, db: Session = Depends(get_db)):
    r = create_reminder(db, title=req.title, remind_at=req.remind_at)
    return {"success": True, "id": r.id, "title": r.title, "remind_at": r.remind_at}

@router.get("/history/{session_id}")
def get_history_endpoint(session_id: str, db: Session = Depends(get_db)):
    return get_conversation_history(db, session_id=session_id)
