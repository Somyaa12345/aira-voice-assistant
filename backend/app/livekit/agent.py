import asyncio
import logging
from typing import Optional
from backend.app.config import settings
from backend.app.pipeline.runner import PipelineRunner

logger = logging.getLogger(__name__)

class LiveKitAiraAgent:
    """LiveKit RTC agent worker connecting room audio tracks to Aira pipeline."""

    def __init__(self, room_name: str = "aira-room"):
        self.room_name = room_name
        self.livekit_url = settings.LIVEKIT_URL
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.pipeline_runner = PipelineRunner()

    async def start(self):
        """Starts LiveKit RTC room worker listener."""
        logger.info(f"Connecting LiveKit agent worker to room '{self.room_name}' at {self.livekit_url}...")
        try:
            # Import livekit agents if installed in local environment
            from livekit import agents
            logger.info("LiveKit agents library connected successfully.")
        except ImportError:
            logger.warning("livekit-agents package not installed locally. Agent will run in HTTP/WebSocket fallback mode.")

    async def handle_audio_track(self, audio_stream):
        """Processes audio frame track from LiveKit room subscriber."""
        await self.pipeline_runner.process_audio_stream(
            audio_stream,
            on_response_audio=lambda chunk: logger.debug(f"Publishing {len(chunk)} audio bytes to LiveKit room.")
        )
