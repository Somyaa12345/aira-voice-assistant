import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database.session import Base, engine, SessionLocal
from backend.app.database.crud import save_memory, get_all_memories, create_note, get_notes, create_reminder, get_pending_reminders
from backend.app.tools.calculator import CalculatorTool
from backend.app.tools.time_tool import TimeTool
from backend.app.tools.app_launcher import AppLauncherTool
from backend.app.assistant.engine import aira_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aira.test_tools_db")

async def test_tools_and_database():
    logger.info("=== Testing Database & Memory Operations ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        mem = save_memory(db, key="user_name", value="Rento", category="preference")
        logger.info(f"Saved memory: {mem.key} -> {mem.value}")

        note = create_note(db, title="Grocery List", content="Milk, Apples, Coffee")
        logger.info(f"Created note: '{note.title}'")

        rem = create_reminder(db, title="Meeting at 4 PM", remind_at="Today 4 PM")
        logger.info(f"Created reminder: '{rem.title}'")

        notes = get_notes(db)
        logger.info(f"Retrieved {len(notes)} notes from database.")
    finally:
        db.close()

    logger.info("=== Testing Tool Execution ===")
    calc = CalculatorTool()
    c_res = await calc.execute(expression="144 / 12 + 88")
    logger.info(f"Calculator Result (144 / 12 + 88): {c_res['result']}")

    tt = TimeTool()
    t_res = await tt.execute()
    logger.info(f"Time Tool Result: {t_res['datetime']}")

    al = AppLauncherTool()
    a_res = await al.execute(app_name="youtube", query="lofi hip hop")
    logger.info(f"App Launcher Result: {a_res['message']} -> {a_res['url']}")

    logger.info("=== Testing Assistant Engine Tool Turn ===")
    query = "What is 15 * 8 and open YouTube for relaxing music?"
    res = await aira_engine.process_text_turn(user_text=query, session_id="test_session")
    logger.info(f"User Query: '{query}'")
    logger.info(f"Assistant Reply: '{res['assistant_reply']}'")
    logger.info(f"Executed Tools: {res['tool_calls']}")

    logger.info("=== ALL DATABASE & TOOL TESTS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(test_tools_and_database())
