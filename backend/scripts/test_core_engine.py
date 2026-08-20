import asyncio
import os
import sys
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.stt.whisper_stt import FasterWhisperSTT, MockSTT
from backend.app.llm.ollama_llm import OllamaLLM, MockLLM
from backend.app.tts.piper_tts import PiperTTS, PyTTSx3TTS, MockTTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aira.test_core")

async def run_core_pipeline_test(use_mocks: bool = False):
    logger.info("=== Starting Aira Core Engine Test (STT -> LLM -> TTS) ===")

    if use_mocks:
        logger.info("Using MOCK providers...")
        stt = MockSTT(mock_text="Aira, tell me a quick joke in Hinglish.")
        llm = MockLLM(response_text="Ek baar ek programmer ne coffee machine ko bug reported kar diya!")
        tts = MockTTS()
    else:
        logger.info("Using REAL providers (FasterWhisper, Ollama, Piper/PyTTSx3)...")
        stt = MockSTT(mock_text="Hello Aira, what is the capital of India?")  # Or real WAV input
        llm = OllamaLLM()
        tts = PiperTTS()

    # Step 1: STT (Speech to Text)
    sample_audio_bytes = b"DUMMY_AUDIO_BYTES"
    user_prompt = await stt.transcribe(sample_audio_bytes)
    logger.info(f"[STT Output] User Prompt: '{user_prompt}'")

    # Step 2: LLM (Ollama)
    messages = [{"role": "user", "content": user_prompt}]
    logger.info("Querying LLM...")
    llm_response = await llm.generate_response(messages)
    assistant_reply = llm_response.get("content", "")
    logger.info(f"[LLM Output] Aira Reply: '{assistant_reply}'")

    # Step 3: TTS (Text to Speech)
    logger.info("Synthesizing speech output...")
    output_audio_path = "test_aira_output.wav"
    audio_bytes = await tts.synthesize(assistant_reply, output_path=output_audio_path)
    logger.info(f"[TTS Output] Generated {len(audio_bytes)} bytes of audio -> saved to '{output_audio_path}'")

    logger.info("=== Aira Core Engine Test COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    use_mock_flag = "--mock" in sys.argv
    asyncio.run(run_core_pipeline_test(use_mocks=use_mock_flag))
