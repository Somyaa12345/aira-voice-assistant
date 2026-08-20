import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.models import Conversation, Memory, Note, Reminder

# --- Conversations ---
def add_conversation(db: Session, role: str, content: str, session_id: str = "default", tool_calls: Optional[List[Dict]] = None) -> Conversation:
    tool_calls_str = json.dumps(tool_calls) if tool_calls else None
    conv = Conversation(
        session_id=session_id,
        role=role,
        content=content,
        tool_calls=tool_calls_str
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_conversation_history(db: Session, session_id: str = "default", limit: int = 20) -> List[Dict[str, str]]:
    convs = db.query(Conversation).filter(Conversation.session_id == session_id).order_by(Conversation.id.desc()).limit(limit).all()
    convs.reverse()
    return [{"role": c.role, "content": c.content} for c in convs]

# --- Memory ---
def save_memory(db: Session, key: str, value: str, category: str = "user_preference") -> Memory:
    existing = db.query(Memory).filter(Memory.key == key).first()
    if existing:
        existing.value = value
        existing.category = category
        db.commit()
        db.refresh(existing)
        return existing

    mem = Memory(key=key, value=value, category=category)
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem

def get_all_memories(db: Session) -> List[Memory]:
    return db.query(Memory).all()

def format_memory_for_prompt(db: Session) -> str:
    memories = get_all_memories(db)
    if not memories:
        return ""
    lines = [f"- {m.key}: {m.value}" for m in memories]
    return "User Long-Term Memory & Preferences:\n" + "\n".join(lines)

# --- Notes ---
def create_note(db: Session, title: str, content: str) -> Note:
    note = Note(title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_notes(db: Session) -> List[Note]:
    return db.query(Note).order_by(Note.created_at.desc()).all()

# --- Reminders ---
def create_reminder(db: Session, title: str, remind_at: str) -> Reminder:
    reminder = Reminder(title=title, remind_at=remind_at)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

def get_pending_reminders(db: Session) -> List[Reminder]:
    return db.query(Reminder).filter(Reminder.is_completed == False).all()
