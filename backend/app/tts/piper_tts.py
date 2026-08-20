import os
import io
import asyncio
import wave
import tempfile
import logging
from typing import AsyncGenerator, Union
from backend.app.tts.base import TTSProvider
from backend.app.config import settings

logger = logging.getLogger(__name__)

class PiperTTS(TTSProvider):
    """Local Text-to-Speech using Piper TTS."""

    def __init__(self, model_path: str = None, config_path: str = None):
        self.model_path = model_path or settings.PIPER_MODEL_PATH
        self.config_path = config_path or settings.PIPER_CONFIG_PATH
        self._voice = None

    def _get_voice(self):
        if self._voice is None:
            try:
                from piper import PiperVoice
                if os.path.exists(self.model_path):
                    self._voice = PiperVoice.load(self.model_path, config_path=self.config_path)
                    logger.info(f"Loaded Piper voice model from {self.model_path}")
                else:
                    logger.warning(f"Piper model not found at {self.model_path}. Will attempt fallback.")
            except ImportError:
                logger.warning("Piper package not installed or model missing.")
        return self._voice

    async def synthesize(self, text: str, output_path: str = None) -> bytes:
        voice = await asyncio.to_thread(self._get_voice)

        if voice is not None:
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wav_file:
                await asyncio.to_thread(voice.synthesize, text, wav_file)
            wav_data = buf.getvalue()
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(wav_data)
            return wav_data

        # Fallback to PyTTSx3 or basic WAV synthesis if Piper is unavailable
        logger.info("Using PyTTSx3 fallback synthesizer.")
        fallback = PyTTSx3TTS()
        return await fallback.synthesize(text, output_path)

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        audio_bytes = await self.synthesize(text)
        # Yield in 4KB chunks
        chunk_size = 4096
        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i : i + chunk_size]

class PyTTSx3TTS(TTSProvider):
    """Fallback offline TTS using pyttsx3 or pure python audio generator."""

    def __init__(self):
        pass

    def _generate_beep_wav(self, duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
        """Generate simple PCM WAV audio bytes as ultimate fallback."""
        import math
        import struct

        num_samples = int(sample_rate * duration_sec)
        frequency = 440.0  # A4 tone
        raw_samples = []

        for i in range(num_samples):
            # Generate sine wave sample
            t = float(i) / sample_rate
            sample_val = int(10000 * math.sin(2.0 * math.pi * frequency * t))
            raw_samples.append(struct.pack('<h', sample_val))

        pcm_data = b''.join(raw_samples)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        return buf.getvalue()

    def _synthesize_to_file(self, text: str, file_path: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            
            # Select Indian female voice if available on system
            voices = engine.getProperty('voices')
            indian_voice = None
            for v in voices:
                v_name = (v.name or "").lower()
                v_id = (v.id or "").lower()
                if any(kw in v_name or kw in v_id for kw in ["heera", "kalpana", "swara", "hindi", "india", "hi_in", "en_in"]):
                    indian_voice = v.id
                    break
            
            if indian_voice:
                engine.setProperty('voice', indian_voice)

            engine.save_to_file(text, file_path)
            engine.runAndWait()
        except Exception as e:
            logger.warning(f"pyttsx3 synthesis failed/unsupported: {e}. Using pure WAV fallback.")
            wav_bytes = self._generate_beep_wav(duration_sec=max(1.0, len(text) * 0.05))
            with open(file_path, "wb") as f:
                f.write(wav_bytes)

    async def synthesize(self, text: str, output_path: str = None) -> bytes:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.close()
        try:
            await asyncio.to_thread(self._synthesize_to_file, text, tmp.name)
            with open(tmp.name, "rb") as f:
                data = f.read()
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(data)
            return data
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        data = await self.synthesize(text)
        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

class MockTTS(TTSProvider):
    """Mock TTS Provider for unit testing."""

    async def synthesize(self, text: str, output_path: str = None) -> bytes:
        # Return dummy WAV header + empty audio bytes
        header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80BB\x00\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        if output_path:
            with open(output_path, "wb") as f:
                f.write(header)
        return header

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        yield await self.synthesize(text)
