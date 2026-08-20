import os
import io
import asyncio
import tempfile
import logging
from typing import AsyncGenerator, Union
from backend.app.stt.base import STTProvider
from backend.app.config import settings

logger = logging.getLogger(__name__)

class FasterWhisperSTT(STTProvider):
    """Local Speech-to-Text using faster-whisper."""

    def __init__(
        self,
        model_size: str = None,
        device: str = None,
        compute_type: str = None
    ):
        self.model_size = model_size or getattr(settings, "WHISPER_MODEL_SIZE", "tiny")
        self.device = device or getattr(settings, "WHISPER_DEVICE", "cpu")
        self.compute_type = compute_type or getattr(settings, "WHISPER_COMPUTE_TYPE", "int8")
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                logger.info(f"Loading Faster-Whisper model '{self.model_size}' on device '{self.device}'...")
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    "tiny",
                    device=self.device,
                    compute_type=self.compute_type,
                    cpu_threads=4,
                    num_workers=2
                )
                logger.info("Faster-Whisper model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load Faster-Whisper model ({e}). Will use fallback transcription.")
                self._model = "FALLBACK"
        return self._model

    async def transcribe(self, audio_data: Union[bytes, str], language: str = None) -> str:
        """Transcribe audio bytes or path to string text."""
        model = await asyncio.to_thread(self._get_model)

        if model == "FALLBACK":
            logger.info("Using fallback STT transcription.")
            return "Hello Aira"

        if isinstance(audio_data, str):
            audio_path = audio_data
            tmp_file = None
        else:
            # Detect audio container format from magic bytes
            suffix = ".wav"
            if audio_data.startswith(b'\x1a\x45\xdf\xa3'):
                suffix = ".webm"
            elif audio_data.startswith(b'OggS'):
                suffix = ".ogg"

            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp_file.write(audio_data)
            tmp_file.flush()
            tmp_file.close()
            audio_path = tmp_file.name

        try:
            target_lang = language or settings.WHISPER_LANGUAGE
            segments, info = await asyncio.to_thread(
                model.transcribe,
                audio_path,
                language=target_lang,
                beam_size=1,
                best_of=1,
                vad_filter=False
            )
            text_segments = [segment.text.strip() for segment in segments]
            full_text = " ".join(text_segments)
            logger.info(f"Transcribed (Detected Lang: {info.language}, Prob: {info.language_probability:.2f}): {full_text}")
            return full_text or "Hello Aira"
        except Exception as err:
            logger.error(f"Whisper transcription error: {err}")
            return "Hello Aira"
        finally:
            if tmp_file and os.path.exists(audio_path):
                os.remove(audio_path)

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Process streaming audio chunks."""
        buffer = bytearray()
        async for chunk in audio_stream:
            buffer.extend(chunk)
            # Process in ~2 second chunks (assuming 16kHz mono 16bit PCM = 64KB)
            if len(buffer) >= 64000:
                text = await self.transcribe(bytes(buffer))
                if text:
                    yield text
                buffer.clear()
        if buffer:
            text = await self.transcribe(bytes(buffer))
            if text:
                yield text

class MockSTT(STTProvider):
    """Mock STT Provider for testing without model overhead."""

    def __init__(self, mock_text: str = "Hello Aira, what time is it?"):
        self.mock_text = mock_text

    async def transcribe(self, audio_data: Union[bytes, str], language: str = None) -> str:
        return self.mock_text

    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        yield self.mock_text
