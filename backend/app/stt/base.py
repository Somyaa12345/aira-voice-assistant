from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Union, BinaryIO

class STTProvider(ABC):
    """Abstract Base Class for Speech-to-Text Providers."""

    @abstractmethod
    async def transcribe(self, audio_data: Union[bytes, str], language: str = None) -> str:
        """Transcribes raw audio bytes or audio file path to text.

        Args:
            audio_data: Audio bytes (WAV/PCM) or file path.
            language: Optional language code ('en', 'hi', etc.).

        Returns:
            Transcribed text string.
        """
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """Transcribes a continuous stream of audio chunks.

        Args:
            audio_stream: Async generator yielding audio bytes.

        Yields:
            Partial or complete text transcripts.
        """
        pass
