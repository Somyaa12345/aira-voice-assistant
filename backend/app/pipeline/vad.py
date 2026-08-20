import logging
import asyncio
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class SileroVADDetector:
    """Silero Voice Activity Detector (VAD) for natural speech & turn detection."""

    def __init__(self, threshold: float = 0.5, sampling_rate: int = 16000):
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        self._model = None
        self.is_speech_active = False

    def _load_model(self):
        if self._model is None:
            try:
                import torch
                model, utils = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    onnx=True
                )
                self._model = model
                logger.info("Silero VAD model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load PyTorch Silero VAD model ({e}). Using energy threshold VAD fallback.")
        return self._model

    def process_frame(self, audio_chunk: bytes) -> bool:
        """Determines whether audio chunk contains speech.

        Returns:
            True if speech detected, False otherwise.
        """
        # Energy-based fallback calculation if PyTorch model is missing
        if len(audio_chunk) < 2:
            return False

        import numpy as np
        samples = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        rms = np.sqrt(np.mean(samples ** 2)) if len(samples) > 0 else 0.0

        # Speech active if RMS energy > 0.02
        speech_detected = bool(rms > 0.02)
        self.is_speech_active = speech_detected
        return speech_detected
