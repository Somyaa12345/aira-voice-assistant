from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from backend.app.assistant.engine import aira_engine
from backend.app.stt.whisper_stt import MockSTT, FasterWhisperSTT
from backend.app.stt import STTProvider
from backend.app.config import settings

router = APIRouter(prefix="/api/voice", tags=["Voice"])

# Lazy-loaded STT provider instance
_stt_provider: STTProvider = None

def get_stt() -> STTProvider:
    global _stt_provider
    if _stt_provider is None:
        try:
            _stt_provider = FasterWhisperSTT()
        except Exception:
            _stt_provider = MockSTT()
    return _stt_provider

@router.post("/process")
async def voice_process_endpoint(
    file: UploadFile = File(...),
    session_id: str = Form("default")
):
    """Accepts uploaded WAV audio file, transcribes with STT, processes turn, and returns synthesized TTS audio response."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file provided.")

    stt = get_stt()
    transcription = await stt.transcribe(audio_bytes)
    
    if not transcription or not transcription.strip() or transcription == "[Silence]":
        transcription = "[Silence]"
        assistant_reply = "I couldn't hear your voice clearly, Somya ji. Please try speaking again!"
        import urllib.parse
        return Response(
            content=f'{{"user_text":"{transcription}","assistant_reply":"{assistant_reply}","tool_calls":[]}}',
            media_type="application/json",
            headers={
                "X-Transcribed-Text": urllib.parse.quote(transcription),
                "X-Assistant-Reply": urllib.parse.quote(assistant_reply)
            }
        )

    result = await aira_engine.process_text_turn(
        user_text=transcription,
        session_id=session_id,
        synthesize_audio=False
    )

    import json, urllib.parse
    resp_body = json.dumps({
        "session_id": session_id,
        "user_text": result["user_text"],
        "assistant_reply": result["assistant_reply"],
        "tool_calls": result.get("tool_calls", [])
    })

    return Response(
        content=resp_body,
        media_type="application/json",
        headers={
            "X-Transcribed-Text": urllib.parse.quote(result["user_text"]),
            "X-Assistant-Reply": urllib.parse.quote(result["assistant_reply"])
        }
    )
