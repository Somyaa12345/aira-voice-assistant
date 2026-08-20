import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.database.session import init_db
from backend.app.api import chat_router, voice_router, tools_router, memory_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aira.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Aira backend database tables...")
    init_db()
    
    # Pre-load STT model into memory on startup
    try:
        from backend.app.api.voice import get_stt
        logger.info("Pre-loading Faster-Whisper STT model into RAM...")
        stt = get_stt()
        stt._get_model()
        logger.info("STT model pre-loaded successfully!")
    except Exception as e:
        logger.warning(f"STT pre-load warning: {e}")

    logger.info(f"Aira Assistant Backend starting up on http://{settings.HOST}:{settings.PORT}")
    yield
    logger.info("Aira Assistant Backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Local-First Personal Voice Assistant API (Ollama + Whisper + Piper)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(tools_router)
app.include_router(memory_router)

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "ollama_model": settings.OLLAMA_MODEL,
        "stt_model": settings.WHISPER_MODEL_SIZE,
        "tts_provider": settings.TTS_PROVIDER
    }

# Mount static frontend files if directory exists
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
