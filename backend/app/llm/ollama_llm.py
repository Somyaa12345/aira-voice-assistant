import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
from backend.app.llm.base import LLMProvider
from backend.app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = """You are Aira, a helpful, friendly, and intelligent voice assistant.
You speak naturally in English, Hindi, or Hinglish depending on what language the user speaks to you.
Keep your spoken responses concise, engaging, and clear (1-3 sentences maximum for voice efficiency).
When using tools, invoke them cleanly.
"""

class OllamaLLM(LLMProvider):
    """Local LLM Provider using Ollama REST API."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate response synchronously via Ollama /api/chat endpoint."""
        endpoint = f"{self.base_url}/api/chat"

        formatted_messages = []
        sys_p = system_prompt or DEFAULT_SYSTEM_PROMPT
        formatted_messages.append({"role": "system", "content": sys_p})
        formatted_messages.extend(messages)

        target_model = self.model or settings.OLLAMA_MODEL
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": False,
            "keep_alive": "60m",
            "options": {
                "temperature": temperature,
                "num_predict": 30,
                "top_k": 20,
                "top_p": 0.9
            }
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

                msg = data.get("message", {})
                content = msg.get("content", "")
                tool_calls = msg.get("tool_calls", None)

                return {
                    "content": content,
                    "tool_calls": tool_calls,
                    "raw": data
                }
            except httpx.HTTPError as err:
                logger.error(f"Ollama API HTTP error: {err}")
                return {
                    "content": "I'm processing your request locally, but my local LLM model took longer than expected to respond. How else can I help?",
                    "tool_calls": None,
                    "error": str(err)
                }

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from Ollama /api/chat endpoint."""
        endpoint = f"{self.base_url}/api/chat"

        formatted_messages = []
        sys_p = system_prompt or DEFAULT_SYSTEM_PROMPT
        formatted_messages.append({"role": "system", "content": sys_p})
        formatted_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("POST", endpoint, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
            except httpx.HTTPError as err:
                logger.error(f"Ollama streaming HTTP error: {err}")
                yield f"I'm sorry, I couldn't reach my local LLM engine. ({err})"

class MockLLM(LLMProvider):
    """Mock LLM Provider for unit testing."""

    def __init__(self, response_text: str = "Hello! I am Aira, your personal voice assistant. How can I help you today?"):
        self.response_text = response_text

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        return {"content": self.response_text, "tool_calls": None}

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        words = self.response_text.split(" ")
        for word in words:
            yield word + " "
