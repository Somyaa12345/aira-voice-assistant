from typing import Dict, Any
from backend.app.tools.base import BaseTool
from backend.app.database.session import SessionLocal
from backend.app.database.crud import create_reminder, get_pending_reminders

class RemindersTool(BaseTool):
    name = "manage_reminders"
    description = "Set a new reminder or list active pending reminders."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list"],
                "description": "Action: 'create' a reminder or 'list' pending reminders"
            },
            "title": {
                "type": "string",
                "description": "What to remind the user about (e.g. 'Call John at 5 PM')"
            },
            "remind_at": {
                "type": "string",
                "description": "When to remind the user (e.g. 'Today 5:00 PM' or 'Tomorrow 10:00 AM')"
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, title: str = "", remind_at: str = "", **kwargs) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            if action == "create":
                if not title:
                    return {"success": False, "error": "Title is required to set a reminder."}
                r = create_reminder(db, title=title, remind_at=remind_at or "Soon")
                return {"success": True, "message": f"Reminder set: '{r.title}' for {r.remind_at}.", "id": r.id}
            elif action == "list":
                reminders = get_pending_reminders(db)
                result = [{"id": r.id, "title": r.title, "remind_at": r.remind_at} for r in reminders]
                return {"success": True, "count": len(result), "reminders": result}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        finally:
            db.close()
