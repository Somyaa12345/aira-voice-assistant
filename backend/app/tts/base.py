from abc import ABC, abstractmethod
from typing import AsyncGenerator, Union

class TTSProvider(ABC):
    """Abstract Base Class for Text-to-Speech Providers."""

    @abstractmethod
    async def synthesize(self, text: str, output_path: str = None) -> bytes:
        """Synthesizes text into audio bytes (WAV format).

        Args:
            text: Text to speak.
            output_path: Optional path to write output file.

        Returns:
            Raw audio bytes (WAV).
        """
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Yields audio chunks for realtime streaming playback."""
        pass
