import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.session import Base
from backend.app.database.crud import (
    save_memory, get_all_memories, create_note, get_notes,
    create_reminder, get_pending_reminders, add_conversation, get_conversation_history
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_memory_crud(db_session):
    mem = save_memory(db_session, key="name", value="Rento", category="user_info")
    assert mem.key == "name"
    assert mem.value == "Rento"
    all_mems = get_all_memories(db_session)
    assert len(all_mems) == 1

def test_notes_crud(db_session):
    note = create_note(db_session, title="Shopping List", content="Milk, Eggs, Bread")
    assert note.title == "Shopping List"
    notes = get_notes(db_session)
    assert len(notes) == 1

def test_reminders_crud(db_session):
    r = create_reminder(db_session, title="Meeting with team", remind_at="5 PM")
    assert r.title == "Meeting with team"
    reminders = get_pending_reminders(db_session)
    assert len(reminders) == 1

def test_conversation_history(db_session):
    add_conversation(db_session, role="user", content="Hello Aira", session_id="s1")
    add_conversation(db_session, role="assistant", content="Hello! How can I help?", session_id="s1")
    hist = get_conversation_history(db_session, session_id="s1")
    assert len(hist) == 2
    assert hist[0]["role"] == "user"
    assert hist[1]["role"] == "assistant"
