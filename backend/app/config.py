import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Aira Voice Assistant"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM (Ollama) Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"

    # STT (Faster-Whisper) Settings
    WHISPER_MODEL_SIZE: str = "tiny"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_LANGUAGE: Optional[str] = "en"  # Enforce English speech recognition

    # TTS Settings
    PIPER_MODEL_PATH: str = "models/en_US-lessac-medium.onnx"
    PIPER_CONFIG_PATH: str = "models/en_US-lessac-medium.onnx.json"
    TTS_PROVIDER: str = "piper"  # 'piper', 'pyttsx3', or 'mock'

    # Database
    DATABASE_URL: str = "sqlite:///./aira.db"

    # LiveKit Settings
    LIVEKIT_URL: str = "ws://localhost:7880"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
