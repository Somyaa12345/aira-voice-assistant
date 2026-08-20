from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.assistant.engine import aira_engine

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    synthesize_audio: Optional[bool] = False

class ChatResponse(BaseModel):
    session_id: str
    user_text: str
    assistant_reply: str
    tool_calls: List[Dict[str, Any]]
    has_audio: bool

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Processes user text query through Aira engine (with memory & tool calling)."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    result = await aira_engine.process_text_turn(
        user_text=request.query,
        session_id=request.session_id,
        synthesize_audio=request.synthesize_audio
    )
    return result
