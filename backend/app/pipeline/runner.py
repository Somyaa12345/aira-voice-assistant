import asyncio
import logging
from typing import AsyncGenerator, Optional, Callable
from backend.app.pipeline.vad import SileroVADDetector
from backend.app.assistant.engine import aira_engine

logger = logging.getLogger(__name__)

class PipelineRunner:
    """Pipecat-inspired voice pipeline runner with VAD and barge-in / interruption handling."""

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.vad = SileroVADDetector()
        self.is_interrupted = False
        self._current_tts_task: Optional[asyncio.Task] = None

    def interrupt(self):
        """Interrupts / barges-in on current TTS playback."""
        if self._current_tts_task and not self._current_tts_task.done():
            logger.info("Barge-in / Interruption triggered! Canceling active TTS playback...")
            self.is_interrupted = True
            self._current_tts_task.cancel()

    async def process_audio_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        on_response_audio: Callable[[bytes], None]
    ):
        """Streams user audio, accumulates speech frame chunks, triggers LLM+TTS on silence."""
        audio_buffer = bytearray()
        silence_frames = 0
        max_silence_frames = 15  # ~1.5 seconds silence to trigger turn completion

        async for chunk in audio_stream:
            # 1. Check for barge-in if assistant is speaking
            is_speech = self.vad.process_frame(chunk)
            if is_speech and self._current_tts_task and not self._current_tts_task.done():
                self.interrupt()

            if is_speech:
                audio_buffer.extend(chunk)
                silence_frames = 0
            elif len(audio_buffer) > 0:
                silence_frames += 1

            # 2. Turn completion triggered by silence after speech
            if silence_frames >= max_silence_frames and len(audio_buffer) > 0:
                logger.info("End of speech turn detected by VAD. Processing user turn...")
                captured_bytes = bytes(audio_buffer)
                audio_buffer.clear()
                silence_frames = 0

                # Transcribe & process turn
                transcription = await aira_engine.stt.transcribe(captured_bytes) if hasattr(aira_engine, 'stt') else "Hello Aira"
                if not transcription.strip():
                    continue

                self.is_interrupted = False
                res = await aira_engine.process_text_turn(transcription, session_id=self.session_id)

                # Synthesize TTS audio response in task that can be interrupted
                async def _stream_tts():
                    try:
                        async for tts_chunk in aira_engine.tts.synthesize_stream(res["assistant_reply"]):
                            if self.is_interrupted:
                                logger.info("TTS stream stopped due to barge-in.")
                                break
                            on_response_audio(tts_chunk)
                            await asyncio.sleep(0.01)
                    except asyncio.CancelledError:
                        logger.info("TTS stream task cancelled by barge-in.")

                self._current_tts_task = asyncio.create_task(_stream_tts())
                await self._current_tts_task
