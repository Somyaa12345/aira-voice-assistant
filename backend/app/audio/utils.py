import io
import wave
import numpy as np

def convert_pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Converts raw PCM audio bytes to WAV formatted bytes."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    return buf.getvalue()

def calculate_audio_energy(audio_bytes: bytes, dtype=np.int16) -> float:
    """Calculates RMS energy of audio frame."""
    if len(audio_bytes) < 2:
        return 0.0
    samples = np.frombuffer(audio_bytes, dtype=dtype).astype(np.float32) / 32768.0
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(samples ** 2)))
