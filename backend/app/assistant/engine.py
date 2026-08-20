import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.llm.base import LLMProvider
from backend.app.llm.ollama_llm import OllamaLLM
from backend.app.tts.base import TTSProvider
from backend.app.tts.piper_tts import PiperTTS
from backend.app.tools.registry import tool_registry
from backend.app.database.session import SessionLocal, init_db
from backend.app.database.crud import add_conversation, get_conversation_history
from backend.app.assistant.memory import MemoryManager

logger = logging.getLogger(__name__)

AIRA_BASE_SYSTEM_PROMPT = """You are Aira, a warm, intelligent, and polite Indian female personal voice assistant.
Language & Tone instructions:
- You MUST communicate EXCLUSIVELY in clean, fluent English.
- Do NOT use Hindi words or Hinglish (no "aapki", "madad", "badiya", "namaste").
- The user's name is Somya. Address her politely as Somya.
- Keep your spoken answers concise, clear, natural, and voice-friendly (1-2 sentences maximum).

Available Tools:
- Use tools whenever needed for math, current time, notes, reminders, or opening YouTube/Spotify/apps.
- When opening YouTube or Spotify, inform the user clearly that you are opening it.

{memory_context}
"""

class AiraAssistant:
    """Core Assistant Engine managing dialogue flow, tool calling, and persistence."""

    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        tts: Optional[TTSProvider] = None
    ):
        self.llm = llm or OllamaLLM()
        self.tts = tts or PiperTTS()
        init_db()

    async def _check_fast_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """Alexa-Class Fast-Path Intent Parser for instant sub-100ms response execution."""
        t = text.lower().strip()
        from datetime import datetime

        # 1. Greetings & Polite Chitchat (0.01s response time)
        if any(t == kw or t == kw + " aira" for kw in ["hi", "hello", "hey", "namaste", "good morning", "good afternoon", "good evening"]):
            reply = "Hello Somya! How can I help you today?"
            return {"reply": reply, "tool": "greeting", "args": {}, "result": {"success": True}}

        if any(kw in t for kw in ["how are you", "how do you do", "how is it going"]):
            reply = "I'm doing great, Somya! How are you doing today?"
            return {"reply": reply, "tool": "greeting", "args": {}, "result": {"success": True}}

        if any(kw in t for kw in ["who are you", "what is your name", "tell me about yourself"]):
            reply = "I am Aira, your local personal voice assistant."
            return {"reply": reply, "tool": "identity", "args": {}, "result": {"success": True}}

        if any(kw in t for kw in ["thank you", "thanks"]):
            reply = "You're very welcome, Somya!"
            return {"reply": reply, "tool": "politeness", "args": {}, "result": {"success": True}}

        if any(t == kw or t == kw + " aira" for kw in ["bye", "goodbye", "see you"]):
            reply = "Goodbye Somya! Have a wonderful day!"
            return {"reply": reply, "tool": "politeness", "args": {}, "result": {"success": True}}

        # 2. Date & Time Intents (Alexa speed!)
        if any(kw in t for kw in ["what time", "current time", "time is it", "time right now"]):
            now_time = datetime.now().strftime("%I:%M %p")
            reply = f"It is {now_time}, Somya."
            return {"reply": reply, "tool": "current_time", "args": {}, "result": {"success": True, "time": now_time}}

        if any(kw in t for kw in ["what date", "today's date", "what day is it", "current date"]):
            now_date = datetime.now().strftime("%A, %B %d, %Y")
            reply = f"Today is {now_date}, Somya."
            return {"reply": reply, "tool": "current_date", "args": {}, "result": {"success": True, "date": now_date}}

        # 3. YouTube Intent (Matches 'youtube', 'yt', 'you to', 'u tube')
        if any(kw in t for kw in ["youtube", "yt", "you to", "u tube"]):
            clean_q = t
            for kw in ["open youtube", "search youtube for", "youtube", "yt", "you to", "u tube", "open", "please", "can you"]:
                clean_q = clean_q.replace(kw, "")
            clean_q = clean_q.strip()
            res = await tool_registry.execute_tool("app_launcher", {"app_name": "youtube", "query": clean_q})
            reply = f"Opening YouTube{' for ' + clean_q if clean_q else ''}, Somya!"
            return {"reply": reply, "tool": "app_launcher", "args": {"app_name": "youtube", "query": clean_q}, "result": res}

        # 4. Spotify & Music Intent
        if any(kw in t for kw in ["spotify", "music", "song"]):
            clean_q = t
            for kw in ["open spotify", "play on spotify", "play music", "spotify", "music", "song", "open", "please", "can you"]:
                clean_q = clean_q.replace(kw, "")
            clean_q = clean_q.strip()
            res = await tool_registry.execute_tool("app_launcher", {"app_name": "spotify", "query": clean_q})
            reply = f"Opening Spotify{' to play ' + clean_q if clean_q else ''}, Somya!"
            return {"reply": reply, "tool": "app_launcher", "args": {"app_name": "spotify", "query": clean_q}, "result": res}

        # 5. Web Search Intent ('search for X', 'google X')
        if any(kw in t for kw in ["search for", "google", "look up"]):
            clean_q = t
            for kw in ["search for", "google", "look up", "search", "please", "can you"]:
                clean_q = clean_q.replace(kw, "")
            clean_q = clean_q.strip()
            if clean_q:
                import urllib.parse
                target_url = f"https://www.google.com/search?q={urllib.parse.quote(clean_q)}"
                import os
                os.system(f'start "" "{target_url}"')
                reply = f"Searching Google for {clean_q}, Somya!"
                return {"reply": reply, "tool": "search", "args": {"query": clean_q}, "result": {"success": True, "url": target_url}}

        # 6. Notes Intent ('note that X', 'add note X', 'show notes')
        if any(kw in t for kw in ["note that", "add note", "take note", "save note"]):
            note_text = t
            for kw in ["note that", "add note", "take note", "save note", "note", "please"]:
                note_text = note_text.replace(kw, "")
            note_text = note_text.strip()
            if note_text:
                res = await tool_registry.execute_tool("notes", {"action": "create", "content": note_text})
                reply = f"Saved note: '{note_text}', Somya!"
                return {"reply": reply, "tool": "notes", "args": {"content": note_text}, "result": res}

        if any(kw in t for kw in ["show notes", "read notes", "my notes"]):
            res = await tool_registry.execute_tool("notes", {"action": "list"})
            notes_list = res.get("notes", [])
            if notes_list:
                items = ", ".join([n.get("content", "") for n in notes_list[:3]])
                reply = f"Here are your latest notes, Somya: {items}."
            else:
                reply = "You have no saved notes, Somya."
            return {"reply": reply, "tool": "notes", "args": {"action": "list"}, "result": res}

        # 7. Reminders Intent ('remind me to X', 'set reminder X')
        if any(kw in t for kw in ["remind me to", "set reminder", "add reminder"]):
            rem_text = t
            for kw in ["remind me to", "set reminder", "add reminder", "reminder", "please"]:
                rem_text = rem_text.replace(kw, "")
            rem_text = rem_text.strip()
            if rem_text:
                res = await tool_registry.execute_tool("reminders", {"action": "create", "title": rem_text})
                reply = f"Reminder set: '{rem_text}', Somya!"
                return {"reply": reply, "tool": "reminders", "args": {"title": rem_text}, "result": res}

        # 8. Weather Intent
        if any(kw in t for kw in ["weather", "temperature", "forecast"]):
            import os
            os.system('start https://www.google.com/search?q=weather')
            reply = "Checking today's weather forecast for you, Somya!"
            return {"reply": reply, "tool": "weather", "args": {}, "result": {"success": True}}

        # 9. Math Intent (e.g. '125 + 75', 'what is 25 * 4')
        import re
        math_match = re.search(r'(\d+\s*[\+\-\*\/\%]\s*\d+)', t)
        if math_match:
            expr = math_match.group(1)
            res = await tool_registry.execute_tool("calculator", {"expression": expr})
            if res.get("success"):
                reply = f"The result of {expr} is {res.get('result')}."
                return {"reply": reply, "tool": "calculator", "args": {"expression": expr}, "result": res}

        return None

    async def process_text_turn(self, user_text: str, session_id: str = "default", synthesize_audio: bool = False) -> Dict[str, Any]:
        """Process a text query through DB memory, LLM, tool execution, and optional TTS."""
        db: Session = SessionLocal()
        try:
            # 1. Save user query to DB
            add_conversation(db, role="user", content=user_text, session_id=session_id)

            # 2. Check for Fast Intent matching (instant zero-latency tool response!)
            fast_match = await self._check_fast_intent(user_text)
            if fast_match:
                logger.info(f"Fast intent matched for query '{user_text}': {fast_match['tool']}")
                assistant_content = fast_match["reply"]
                executed_tools = [{
                    "tool": fast_match["tool"],
                    "args": fast_match["args"],
                    "result": fast_match["result"]
                }]
            else:
                # 3. Retrieve history & memory context for LLM (limit=3 for sub-second prompt evaluation!)
                history = get_conversation_history(db, session_id=session_id, limit=3)
                memory_str = MemoryManager.get_system_prompt_context(db)
                system_prompt = AIRA_BASE_SYSTEM_PROMPT.format(memory_context=memory_str)

                # 4. Format messages for LLM
                messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
                
                # Only include heavy tool schemas if query specifically mentions supported tool action keywords
                tool_keywords = ["note", "remind", "time", "calc", "math", "youtube", "spotify", "weather"]
                user_query_lower = user_text.lower()
                needs_tools = any(kw in user_query_lower for kw in tool_keywords)
                tools_schema = tool_registry.get_ollama_schemas() if needs_tools else None

                # 5. Call LLM
                logger.info(f"Sending turn to LLM (session '{session_id}', with_tools={needs_tools})...")
                llm_result = await self.llm.generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    tools=tools_schema
                )

                assistant_content = llm_result.get("content", "")
                tool_calls = llm_result.get("tool_calls", None)
                executed_tools = []

                # Handle case where Ollama outputs raw JSON tool call string into content
                if assistant_content and assistant_content.strip().startswith("{") and ("\"function\"" in assistant_content or "\"name\"" in assistant_content):
                    try:
                        parsed_json = json.loads(assistant_content.strip())
                        fn_data = parsed_json.get("function", parsed_json)
                        t_name = fn_data.get("name")
                        t_args = fn_data.get("parameters", fn_data.get("arguments", {}))
                        if t_name:
                            tool_calls = [{"function": {"name": t_name, "arguments": t_args}}]
                            assistant_content = ""
                    except Exception as parse_err:
                        logger.warning(f"Failed to parse raw JSON tool call from LLM content: {parse_err}")

                # Handle Tool Calls if triggered by LLM
                if tool_calls:
                    logger.info(f"LLM requested tool execution: {tool_calls}")
                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        t_name = fn.get("name")
                        t_args = fn.get("arguments", {})
                        if isinstance(t_args, str):
                            try:
                                t_args = json.loads(t_args)
                            except Exception:
                                t_args = {}

                        t_result = await tool_registry.execute_tool(t_name, t_args)
                        executed_tools.append({
                            "tool": t_name,
                            "args": t_args,
                            "result": t_result
                        })

                    # Formulate conversational response after tool execution
                    if executed_tools:
                        last_t = executed_tools[-1]
                        if last_t["tool"] == "app_launcher":
                            app_name = last_t["args"].get("app_name", "app")
                            assistant_content = f"Opening {app_name} for you, Somya!"
                        elif last_t["tool"] == "calculator":
                            assistant_content = f"The calculation result is {last_t['result'].get('result')}."
                        elif last_t["tool"] == "current_time":
                            assistant_content = last_t["result"].get("message", "Here is the current time.")
                        else:
                            assistant_content = f"Done! Executed {last_t['tool']} for you, Somya."

            # 6. Save assistant response to DB
            add_conversation(db, role="assistant", content=assistant_content, session_id=session_id, tool_calls=executed_tools)

            # 7. Synthesize audio if requested
            audio_bytes = None
            if synthesize_audio and assistant_content:
                audio_bytes = await self.tts.synthesize(assistant_content)

            return {
                "session_id": session_id,
                "user_text": user_text,
                "assistant_reply": assistant_content,
                "tool_calls": executed_tools,
                "has_audio": audio_bytes is not None,
                "audio_bytes_length": len(audio_bytes) if audio_bytes else 0
            }

        finally:
            db.close()

aira_engine = AiraAssistant()
