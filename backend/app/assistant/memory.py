import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.crud import save_memory, get_all_memories, format_memory_for_prompt

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages long-term user memories and facts."""

    @staticmethod
    def remember(db: Session, key: str, value: str, category: str = "preference") -> Dict[str, Any]:
        mem = save_memory(db, key=key, value=value, category=category)
        logger.info(f"Saved memory: {key} = {value}")
        return {"key": mem.key, "value": mem.value, "category": mem.category}

    @staticmethod
    def get_system_prompt_context(db: Session) -> str:
        return format_memory_for_prompt(db)
